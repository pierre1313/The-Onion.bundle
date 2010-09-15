from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *
import re

TO_PLUGIN_PREFIX   = "/video/theonion"
TO_BASE_URL        = "http://www.theonion.com"
#TO_SEARCH_URL      = HULU_BASE_URL + "search/"

CACHE_INTERVAL       = 1000 # HTTP cache interval in seconds
MAX_RESULTS          = "100"

TO_AJAX              = "http://www.theonion.com/ajax/onn_playlist/%s/%s" #% show name %pagenum

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
def populateFromHTML(sender, show_id, show_title = '', replaceParent = False,  page=1):

  dir = MediaContainer(content = 'Items', viewGroup="List", replaceParent = replaceParent, title2=str(show_title) + ' - Page '+str(page))
  
  if page>1 :
    dir.Append(Function(DirectoryItem(populateFromHTML, title = 'Previous Page ...'),show_id = show_id, page = page-1, replaceParent = True))
  
  for e in XML.ElementFromURL(TO_AJAX % (show_id,page), CACHE_INTERVAL).xpath("//li"):
    id = TO_BASE_URL + e.xpath("div[@class='image_wrapper']//a")[0].get("href")
    thumb = e.xpath("div[@class='image_wrapper']//a/img")[0].get("src")
    title = e.xpath("p/a")[0].text
    try:
      duration = e.xpath("p/span[@class='date']")[0].text.replace("(","").replace(")","")
      (mins, secs) = duration.split(":")
      if mins == "" or mins == " ": mins = 0
      else: mins = int(mins)
      duration = str(((mins * 60) + int(secs)) * 1000)
    except:
      duration = ""
    html = HTTP.Request(id)  
    link_pattern = re.compile('var video_url = "([^"]+)"')
    link = link_pattern.search(html)
    if link != None:
      link = link.group(1)
    dir.Append(VideoItem(link, title,'',summary ='', duration = duration, thumb=thumb))
  dir.Append(Function(DirectoryItem(populateFromHTML, title = 'Next Page ...'),show_id = show_id, show_title = show_title, page = page+1, replaceParent = True))
  return dir
    
def MainMenu():
   dir = MediaContainer(title2='')  

   categories = XML.ElementFromURL("http://www.theonion.com/content/video", cacheTime=CACHE_INTERVAL, isHTML=True).xpath('//ul[@id="categories"]/li')
   for e in categories:
     id = e.get("id")
     cls = e.get("class")
     if cls == "category":   
       dir.Append(Function(DirectoryItem(Shows,title = "Shows")))
       break
     else:
       title = e.xpath("a")[0].get("rel")
       dir.Append(Function(DirectoryItem(populateFromHTML,title = title),show_id = id, show_title = title))
   return dir
   
def Shows(sender):
   dir = MediaContainer(title2='Shows')  

   shows = XML.ElementFromURL("http://www.theonion.com/content/video", cacheTime=CACHE_INTERVAL, isHTML=True).xpath('//ul[@id="categories"]/li')
   foundshow = 0
   for e in shows:
     id = e.get("id")
     cls = e.get("class")
     if cls == "category":
       foundshow = 1
     else:   
       if foundshow == 1:
         try:
           title = e.xpath("a")[0].get("rel")
         except:
           title = e.xpath("span/a")[0].get("rel")
         dir.Append(Function(DirectoryItem(populateFromHTML,title = title),show_id = id, show_title = title))
   return dir
