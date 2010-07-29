from PMS import Plugin, Log, XML, HTTP, JSON, Prefs, RSS, Utils
from PMS.MediaXML import *
from PMS.Shorthand import _L, _R, _E, _D

TO_PLUGIN_PREFIX   = "/video/theonion"
TO_BASE_URL        = "http://www.theonion.com/"
#TO_SEARCH_URL      = HULU_BASE_URL + "search/"

CACHE_INTERVAL       = 1000 # HTTP cache interval in seconds
MAX_RESULTS          = "100"

TO_AJAX              = "http://www.theonion.com/content/ajax/onn/list/%s/1/%s" # % max_results % show name

####################################################################################################
def Start():
  Plugin.AddRequestHandler(TO_PLUGIN_PREFIX, HandleRequest, "The Onion", "icon-default.jpg", "art-default.jpg")
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", contentType="items")  
  Plugin.AddViewGroup("List", viewMode="List", contentType="items")
####################################################################################################
def populateFromHTML(show_id, dir, title2=""):
  dir.SetViewGroup("InfoList")
  for e in XML.ElementFromString(HTTP.GetCached(TO_AJAX % (MAX_RESULTS, show_id), CACHE_INTERVAL), True).xpath("//li"):
    id = TO_BASE_URL + e.xpath("div[@class='image_wrapper']//a")[0].get("href")
    thumb = e.xpath("div[@class='image_wrapper']//a/img")[0].get("src")
    title = e.xpath("div[@class='image_wrapper']//img")[0].get("title")
    desc = e.xpath("p/a")[0].text
    try:
      duration = e.xpath("p/span[@class='date']")[0].text.replace("(","").replace(")","")
      (mins, secs) = duration.split(":")
      if mins == "" or mins == " ": mins = 0
      else: mins = int(mins)
      duration = str(((mins * 60) + int(secs)) * 1000)
    except:
      duration = ""
    dir.AppendItem(WebVideoItem(id, title, desc, duration, thumb))
  return dir
    
def HandleRequest(pathNouns, count):
  i=0
  for x in pathNouns:
    Log.Add(str(i) + ": " + x)
    i+=1
    
  try:
    (pathNouns[count-1], title2) = pathNouns[count-1].split("||")
  except:
    title2 = ""
  
  dir = MediaContainer("art-default.jpg", viewGroup="List", title1="The Onion", title2=title2)  
  if count == 0:
    for e in XML.ElementFromString(HTTP.GetCached("http://www.theonion.com/content/video", CACHE_INTERVAL), True).xpath('//ul[@id="categories"]/li'):  
      id = e.get("id")
      cls = e.get("class")
      if cls != "category":
        title = e.xpath("a")[0].text
        dir.AppendItem(DirectoryItem("videolist^" + id + "||" + _L(title), _L(title), ""))
      else:
        dir.AppendItem(DirectoryItem(e.text + "||" + _L(e.text), _L(e.text), ""))
        break
      
  elif pathNouns[-1].startswith("Shows"):
    foundShow=0
    for e in XML.ElementFromString(HTTP.GetCached("http://www.theonion.com/content/video", CACHE_INTERVAL), True).xpath('//ul[@id="categories"]/li'): 
      id = e.get("id")
      cls = e.get("class")
      if foundShow == 0:
        if cls == "category":
          foundShow = 1
      else:
        try:
          title = e.xpath("a")[0].get("rel")
        except:
          title = e.xpath("span/a")[0].get("rel")
        show_id = title.replace("-","").replace(" ","")
        if show_id == "Election08":
          show_id = "election"
        dir.AppendItem(DirectoryItem("videolist^" + show_id + "||" + _L(title), _L(title), ""))
        
  elif pathNouns[-1].startswith("videolist"):
    show_id = pathNouns[-1].split("^")[1].lower()
    dir = populateFromHTML(show_id, dir)

  return dir.ToXML()