import re

TO_PLUGIN_PREFIX   = "/video/theonion"
TO_BASE_URL        = "http://www.theonion.com"

CACHE_INTERVAL       = 1000 # HTTP cache interval in seconds
MAX_RESULTS          = "100"

MAIN_PAGE            = "http://www.theonion.com/content/video"
TO_AJAX              = "http://www.theonion.com/ajax/onn_playlist/%s/%s" #% show name %pagenum
JSONPATH             = "http://www.theonion.com/ajax/onn/embed/%s.json"

ART = "art-default.jpg"
NAME = "The Onion"
ICON = "icon-default.jpg"

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(TO_PLUGIN_PREFIX, MainMenu, NAME, ICON, ART)
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")  
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
  MediaContainer.art = R(ART)
  MediaContainer.title1 = NAME
  MediaContainer.viewGroup = "List"

  # Default icons for DirectoryItem
  DirectoryItem.thumb = R(ICON)
  
####################################################################################################
def GetThumb(sender,url):
  return DataObject(HTTP.Request(url),'image/jpg')

def populateFromHTML(sender, show_id, show_title = '', replaceParent = False,  page=1):

  dir = MediaContainer(content = 'Items', viewGroup="InfoList", replaceParent = replaceParent, title2=str(show_title) + ' - Page '+str(page))
  
  if page>1 :
    dir.Append(Function(DirectoryItem(populateFromHTML, title = 'Previous Page ...'),show_id = show_id, page = page-1, replaceParent = True))
  
  for e in XML.ElementFromURL(TO_AJAX % (show_id,page), CACHE_INTERVAL).xpath("//li"):
    elementid = TO_BASE_URL + e.get("class")
    id = elementid[elementid.rfind('_')+1:]
    summary = e.xpath("//p[@class='teaser']")[0].text
    jsonObject = JSON.ObjectFromURL(JSONPATH % id)
    link = jsonObject['video_url']
    title = jsonObject['title']
    duration = jsonObject['duration']
    thumb = jsonObject['thumbnail']
    dir.Append(VideoItem(link, title,'',summary = summary, duration = duration, thumb=Function(GetThumb,thumb)))
  dir.Append(Function(DirectoryItem(populateFromHTML, title = 'Next Page ...'),show_id = show_id, show_title = show_title, page = page+1, replaceParent = True))
  return dir
    
def MainMenu():
   dir = MediaContainer(title2='')  
   
   dir.Append(Function(DirectoryItem(Shows,title = "Shows")))
   categories = HTML.ElementFromURL(MAIN_PAGE, cacheTime=CACHE_INTERVAL).xpath('//div[@id="side_recirc"]/div')
   for c in categories:
     id = c.get("rel")
     title = c.xpath("a")[0].text
     dir.Append(Function(DirectoryItem(populateFromHTML,title = title),show_id = id, show_title = title))
   return dir
   
def Shows(sender):
   dir = MediaContainer(title2='Shows')  

   shows = HTML.ElementFromURL(MAIN_PAGE, cacheTime=CACHE_INTERVAL).xpath('//ul[@id="categories"]//li')
   for e in shows:
     if e.get("class") != "label":
       title= e.xpath("a")[0].text_content()
       id = e.get("rel")
       dir.Append(Function(DirectoryItem(populateFromHTML,title = title),show_id = id, show_title = title))
   return dir
