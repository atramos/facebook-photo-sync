#!/usr/bin/python2

import facebook
import sys
import os
import urllib2
import yaml

class FB:
  def __init__(self):
    pass

  def getToken(self):
    """Go to https://developers.facebook.com/tools/explorer/
    Click 'Get Access Token', and select user_photos then continue.
    Your token will be in the text box, please copy it.
    When you've copied it, please enter it below."""
    try:
      self.token = raw_input("Access Token: ").strip()
    except Exception as error:
      print "Could not handle input: %s\nQuitting!" % (error)
      sys.exit(1)

  def auth(self, token=""):
    if token != "":
      try:
        self.graph = facebook.GraphAPI(token)
      except Exception as error:
        print error
        sys.exit(1)
    else:
      print "Empty token"
      sys.exit(1)

  def get_albums(self):
    self.albums = self.graph.get_object("me/albums")

  def get_album_pics(self, album_name, album_id):
    if not os.path.isdir("%s" % (album_name)):
      os.mkdir("%s" % (album_name))
    self.album_pics = self.graph.get_object("%s/photos" % (album_id))

    for album_pic in self.album_pics["data"]:
      like_count = 0
      like_names = []
      comments = {}
      try:
        image_data = urllib2.urlopen(album_pic["source"]).read()
      except Exception as error:
        print error
        sys.exit(1)

      try:
        image = open("%s/%s.jpg" % (str(album_name), str(album_pic["id"])), "wb")
        image.write(image_data)
        image.close()
      except Exception as error:
        print error
        sys.exit(1)


      try:
        for like in album_pic["likes"]["data"]:
          like_count += 1
      except:
        pass

      try:
        if album_pic["comments"]:
          for comment in album_pic["comments"]["data"]:
            comments[comment["from"]["name"]] = comment["message"]
      except:
        pass

      try:
        if album_pic["likes"]:
          for like in album_pic["likes"]["data"]:
            like_names.append(like["name"])
      except Exception as error:
        print error

      yaml_data = {"comments": {}, "likes": {}}

      #like count
      yaml_data["like_count"] = like_count


      #comments
      count = 0
      for comment in comments:
        comment_name = comment
        comment_text = comments[comment]
        yaml_data["comments"]["comment%s" % count] = "%s:%s" % (comment_name, comment_text.rstrip())
        count += 1

      #likes 
      count = 0
      for like in like_names:
        like_name = like
        yaml_data["likes"]["like%s" % count] = like_name
        count += 1

      #title
      try:
        yaml_data["title"] = album_pic["name"]
      except:
        yaml_data["title"] = "None"


      yaml_file = open("%s/%s.yaml" % (str(album_name), str(album_pic["id"])), "w")
      yaml_file.write(yaml.safe_dump(yaml_data, default_flow_style=False))
      yaml_file.close()

      print "[*] Downloaded \"%s.jpg\" to the \"%s\" folder! Likes: %s" % (album_pic["id"], album_name, like_count)



if __name__ == "__main__":
  FB = FB()
  FB.getToken()
  FB.auth(FB.token)

  print "[*] Retrieving Album Names ..."
  FB.get_albums()
  print "[*] Album Names retrieved ...\n"

  album_download = raw_input("Album to download: ")
  if len(album_download) != 0:
    album_found = False
    try:
      for album in FB.albums["data"]:
        if album["name"] == album_download:
          album_found = True
          album_id = album["id"]
          print "\n[*] Album found.. Starting download.\n"
      if album_found == False:
        print "[!] Album not found...Quitting!"
        sys.exit(0)
    except Exception as error:
      print error
      sys.exit(1)
  else:
    print "[!] Error, album name empty.\nQuitting!"
    sys.exit(0)

  FB.get_album_pics(album_download, album_id)