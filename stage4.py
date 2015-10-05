import webapp2, urllib, jinja2, os
import time
             
from google.appengine.ext import ndb
from google.appengine.api import users


GUEST_NAME = "default_guest"
 
ERROR_HTML = """ 
<br><br><b><form> <font size="6"> Invalid title and description. 
<br>Click back to return and retry.</font> </b></form>
""" 

def guest_key(guest_name=GUEST_NAME):
    """Constructs a Datastore key for a guest entity.

    We use guest_name as the key.
    """
    return ndb.Key('guest', guest_name)
# [START comment]
# These are the objects that will represent our Author and our Post. We're using
# Object Oriented Programming to create objects in order to put them in Google's
# Database. These objects inherit Googles ndb.Model class.
class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)

class Comment(ndb.Model):
    author = ndb.StructuredProperty(Author)
    title = ndb.StringProperty(indexed=False)
    description = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

# [END comment]
class MainPage(webapp2.RequestHandler):
    def get(self):
       error = self.request.get('error','')
       guest_name = self.request.get('guest_name', GUEST_NAME)
       # Query commments and display by time
       comments_query = Comment.query(
               ancestor=guest_key(guest_name)).order(-Comment.date)
       comments = comments_query.fetch(10)
        
       # If a person is logged in to Google's Services
       user = users.get_current_user()
       if user:
           url = users.create_logout_url(self.request.uri)
           url_linktext = 'Logout'
       else:
       # User will need to login
           url = users.create_login_url(self.request.uri)
           url_linktext = 'Login'

       # These are the values to be passed to template
       template_values = {
        'user': user,
        'comments': comments,
        'guest_name': urllib.quote_plus(guest_name),
        'url': url,
        'url_linktext': url_linktext,
        }
       template_dir = os.path.join(os.path.dirname(__file__),'templates')
       jinja_env = jinja2.Environment(
            loader = jinja2.FileSystemLoader(template_dir),
            autoescape = True)
       template = jinja_env.get_template('notes.html')

       self.response.write(template.render(template_values))
 
    
    def post(self):
    # We set the same parent key on the 'Comment' to ensure each
    # Comment is in the same entity group. Queries across the
    # single entity group will be consistent. 
    #
        guest_name = self.request.get('guest_name', GUEST_NAME)
        comment = Comment(parent=guest_key(guest_name))
         
        if users.get_current_user():
            comment.author = Author(
               identity=users.get_current_user().user_id(),
                email=users.get_current_user().email())

 # Get the description from our request parameters, 
 # "title" and "description".
        comment.title = self.request.get('title')
        comment.description = self.request.get('description')
        
        if comment.title.strip() and comment.description.strip():  
            # if title and description are valid 
            #  load data to Google Datastore
            time.sleep(1)
            comment.put()
            query_params = {'guest_name': guest_name}
            self.redirect('/?' + urllib.urlencode(query_params))
        else:
            # Error, title or description not valid.
            time.sleep(.1)
            self.response.out.write(ERROR_HTML)
            # Do not put in Datastore.                 
# [END main_page]

app = webapp2.WSGIApplication([
   ('/', MainPage),
], debug=True)
