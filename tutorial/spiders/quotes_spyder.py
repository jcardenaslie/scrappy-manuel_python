import scrapy
import pandas as pd
from bs4 import BeautifulSoup

class QuotesSpider(scrapy.Spider):
	name = 'ruts' #spider name
	count = 0
	data =[] 
	test_searches = [] 
	searches = []
	
	def start_requests(self):
		
		datos = pd.read_csv('C:/Users/jquin/Desktop\manuel/scrapy_project/tutorial/rut.csv')
		datos=datos[66:]
		datos = datos.as_matrix()

	
		for element in datos:
		    string =str(element[0])+str(element[1])
		    self.searches.append(string)

		# self.test_searches = self.searches[0:20]

		urls = []
		for search in self.searches:
		    urls.append('https://www.mercantil.com/SE/results.asp?keywords='+search)

		for url in urls:
			yield scrapy.Request(url=url,dont_filter=True, callback=self.parse, meta = {
                      'dont_redirect': True,
                      'handle_httpstatus_list': [302]
                  })

	def parse(self,response):
		# filename = 'ruts/{}'.format(self.count)
		
		# with open(filename, 'wb') as f:
		# 	f.write(response.body)
		# self.log('Saved file {}'.format(filename))
		
		try:
			soup = BeautifulSoup(response.body,"lxml")
			name = soup.title.string.split("-")[0]
			rut = ''

			divs = soup.find_all('div', class_='separador_mobile')

			for div in divs:
				if div.p.text == 'Rut':
					rut = ('').join(div.span.text.split('-'))
					self.log('RUT: {}'.format(rut))
			
			self.log('NAME: {}'.format(name))


			if name == '500':
			    name = 'no disponible'
			
			     
			self.data.append([rut,name])
			df = pd.DataFrame(self.data)
			df.to_csv('ruts_spider.csv', index=False, header=['Rut','Nombre'])
			self.log('Saved file')
		except:
			self.log('HUBO UN ERROR ERROR ERROR')
		    # continue

		self.count += 1