from mcb.services import Service
from mcb.services.email import EmailImapService

import requests
from bs4 import BeautifulSoup

from pprint import pprint

class GoogleHack(Service):

  loginUrl = 'https://accounts.google.com/ServiceLogin'

  def __init__(self):
    super(GoogleHack, self).__init__()
    self.addConfig('email', 'Email')
    self.addConfig('password', 'Password')

  def getPluginOutputPrefix(self):
    return self.email.replace('@', '_at_')

  def login(self):
    self.session = session = requests.Session()
    response = session.get(self.loginUrl)

    soup = BeautifulSoup(response.text)

    data = {}

    form = soup.find('form', id='gaia_loginform')

    for inp in form.find_all('input', type='hidden'):
      data[inp.attrs['name']] = inp.attrs['value']

    data['Email'] = self.email
    data['Passwd'] = self.password

    url = form.attrs['action']

    response = session.post(url, data)

    if not response.text.find('Connected accounts'):
      raise Exception('Login failed')


class CalendarService(GoogleHack):

  exportUrl = 'https://www.google.com/calendar/exporticalzip'


  def setup(self):
    self.name = 'google.calendar'
    self.pretty_name = 'Google Calendar'

  def getId(self):
    return self.name + '_' + self.email

  def getPrettyId(self):
    return self.pretty_name + ' - ' + self.email 

  def runBackup(self):
    self.login()
    response = self.session.get(self.exportUrl)

    if response.url.find('ServiceLogin') != -1:
      raise Exception('Could not log in to Google. Check credentials.')

    self.output.set('calendars.zip', response.content)

class GmailService(EmailImapService):
  """Imap imported customized for Gmail, to prevent duplicate messages
  A lot more coud be done here, this is just preliminary:
  Problem: Gmail supplies each tag as a separate IMAP folder, so messages
  get duplicated multiple times.

  For now we just use the [Gmail]/All folder
  This does not allow to restore the tag structure properly though!
  """

  def setup(self):
    super(GmailService, self).setup()

    self.name = 'google.gmail'
    self.pretty_name = 'Google Mail'

    self.host = 'imap.gmail.com'
    host = self.getConfigItem('host')
    host['default'] = self.host
    host['internal'] = True

    self.port = 993
    port = self.getConfigItem('port')
    port['default'] = 993
    port['internal'] = True

    self.ssl = True
    ssl = self.getConfigItem('ssl')
    ssl['default'] = True
    ssl['internal'] = True

  def getId(self):
    return self.name + '_' + self.username

  def getPrettyId(self):
    return self.pretty_name + ' - ' + self.username 

  def getFolders(self):
    return ['[Gmail]/All Mail']
