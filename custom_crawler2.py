from urllib.request import Request, urlopen
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random
import pandas as pd

ua = UserAgent() # From here we generate a random user agent
proxies = [] # Will contain proxies [ip, port]
data = []
# Main function

def get_proxy(proxies):
  proxy_index = random_proxy(proxies)
  proxy = proxies[proxy_index]
  proxy_string = proxy['ip'] + ':' + proxy['port']
  return proxy_string, proxy_index, proxy

def main():
  
  proxies = find_proxies()

  proxy_string, proxy_index, proxy = get_proxy(proxies)
  
  urls = target_urls(start_index=2432)
  
  n = 0
  

  for url in urls:
    keep_trying = True
    
    while keep_trying:
      print('')
      print(url[1])
      print('Using: {}'.format(proxy_string))
      
      try:
        
        req = Request(url[1])
        req.set_proxy(proxy_string, 'http')

        my_ip = urlopen(req).read().decode('utf8')

        success = save_to_csv(my_ip,url[0], success=True)
        

        keep_trying = False

        if success == False:
          print('REDIRECTED')
          proxy_string, proxy_index, proxy = get_proxy(proxies)
          keep_trying = True
      except urllib.error.URLError as e: # If error, delete this proxy and find another one
        print(str(e.reason))
        
        if str(e.reason)== 'Internal Server Error':
          save_to_csv('No disponible',url[0], success=False)
          keep_trying = False
          break
        
        del proxies[proxy_index]
        
        print('Proxy ' + proxy['ip'] + ':' + proxy['port'] + ' deleted.')
        
        proxy_string, proxy_index, proxy = get_proxy(proxies)

# Retrieve a random index proxy (we need the index to delete it if not working)
def random_proxy(proxies):
  return random.randint(0, len(proxies) - 1)


def save_to_csv(string,rut_id, success=True):
  
  if success:
    soup = BeautifulSoup(string,"lxml")
    name = soup.title.string.split("-")[0]
    
    if name == 'mercantil.com el portal de negocios lider en Chile':
      print('REDIRECTED')
      return False

    rut = ''

    divs = soup.find_all('div', class_='separador_mobile')

    for div in divs:
      if div.p.text == 'Rut':
        rut = ('').join(div.span.text.split('-'))
        print('RUT: {}'.format(rut))
          
    print('NAME: {}'.format(name))
  else:
    rut = rut_id
    name = string
  
  global data        
  data.append([rut_id,name])
  df = pd.DataFrame(data)
  df.to_csv('ruts_nombres13.csv', index=False, header=['Rut','Nombre'])
  print('Saved file')
  return True


def find_proxies():
  # Retrieve latest proxies
  proxies_req = Request('https://www.sslproxies.org/')
  proxies_req.add_header('User-Agent', ua.random)
  proxies_doc = urlopen(proxies_req).read().decode('utf8')

  soup = BeautifulSoup(proxies_doc, 'html.parser')
  proxies_table = soup.find(id='proxylisttable')
  
  # Save proxies in the array
  proxies = []
  
  for row in proxies_table.tbody.find_all('tr'):
    proxies.append({
      'ip':   row.find_all('td')[0].string,
      'port': row.find_all('td')[1].string
    })
  
  assert (len(proxies) > 0)

  return proxies

def target_urls(start_index = 0):
  datos = pd.read_csv('rut.csv')
  # datos=datos[66:]
  datos = datos.as_matrix()
  searches = []
  
  for element in datos:
      string =str(element[0])+str(element[1])
      searches.append(string)

  # test_searches = searches[0:20]

  urls = []
  searches = searches[start_index:]
  for search in searches:
      rut = search
      url = 'https://www.mercantil.com/SE/results.asp?keywords='+search
      urls.append((rut,url))

  return urls


if __name__ == '__main__':
  main()