from urllib.request import Request, urlopen
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random
import pandas as pd

ua = UserAgent() # From here we generate a random user agent
proxies = [] # Will contain proxies [ip, port]

# Main function
def main():
  # Retrieve latest proxies
  proxies_req = Request('https://www.sslproxies.org/')
  proxies_req.add_header('User-Agent', ua.random)
  proxies_doc = urlopen(proxies_req).read().decode('utf8')

  soup = BeautifulSoup(proxies_doc, 'html.parser')
  proxies_table = soup.find(id='proxylisttable')

  # Save proxies in the array
  for row in proxies_table.tbody.find_all('tr'):
    proxies.append({
      'ip':   row.find_all('td')[0].string,
      'port': row.find_all('td')[1].string
    })

  # Choose a random proxy
  proxy_index = random_proxy()
  proxy = proxies[proxy_index]


  datos = pd.read_csv('C:/Users/joaquin/Desktop/tutorial/rut.csv')
  datos=datos[66:]
  datos = datos.as_matrix()
  searches = []
  
  for element in datos:
      string =str(element[0])+str(element[1])
      searches.append(string)

  test_searches = searches[0:20]

  urls = []
  for search in test_searches:
      urls.append('https://www.mercantil.com/SE/results.asp?keywords='+search)

  # for n in range(1, 100):
  n = 0
  data = []
  for url in urls:
    print(url)
    # req = Request('http://icanhazip.com')
    req = Request(url)
    req.set_proxy(proxy['ip'] + ':' + proxy['port'], 'http')

    # Every 10 requests, generate a new proxy
    if n % 10 == 0:
      proxy_index = random_proxy()
      proxy = proxies[proxy_index]
      n+=1
    # Make the call
    try:
      my_ip = urlopen(req).read().decode('utf8')

      soup = BeautifulSoup(my_ip,"lxml")
      name = soup.title.string.split("-")[0]
      rut = ''

      divs = soup.find_all('div', class_='separador_mobile')

      for div in divs:
        if div.p.text == 'Rut':
          rut = ('').join(div.span.text.split('-'))
          print('RUT: {}'.format(rut))
      
      print('NAME: {}'.format(name))


      if name == '500':
          name = 'no disponible'
      
           
      data.append([rut,name])
      df = pd.DataFrame(data)
      df.to_csv('ruts_nombres.csv', index=False, header=['Rut','Nombre'])
      print('Saved file')



      # print('#' + str(n) + ': ' + my_ip)
    except urllib.error.URLError as e: # If error, delete this proxy and find another one
      print(str(e.reason))
      del proxies[proxy_index]
      print('Proxy ' + proxy['ip'] + ':' + proxy['port'] + ' deleted.')
      proxy_index = random_proxy()
      proxy = proxies[proxy_index]

# Retrieve a random index proxy (we need the index to delete it if not working)
def random_proxy():
  return random.randint(0, len(proxies) - 1)

if __name__ == '__main__':
  main()