from bs4 import BeautifulSoup
import requests, lxml, os
import pandas as pd
from pandas import ExcelWriter



#install:
#pip install -r requirements.txt


search_word="umanizales.edu.co"
search_link="https://scholar.google.com/citations?view_op=search_authors&hl=es&mauthors="




#Description: Metodo para escribir el resultado y exportar arhcivo excel con datos
#params: dict(diccionario con datos del docente)
def write_results(dict):
    df=pd.DataFrame.from_dict(dict["profiles"])
    writer = pd.ExcelWriter('Profesores_IndiceH.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    #print(profile["name"])

    writer.save()
    print("Guardo el Archivo con informacion de Profesores")





#Description: Metodo para obtener datos de perfiles
#Params : profiles(Lista con los ids de los perfiles)
def get_inf_author(profiles):
    dict_frame={"profiles":[]}
    #Setting search
    headers = {
    'User-agent':
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
    }
    proxies = {
    'http': os.getenv('HTTP_PROXY')
    }
    print('Author info:')
    
    for id in profiles:
        html = requests.get(f'https://scholar.google.com/citations?hl=en&user={id}', headers=headers,
        proxies=proxies)
        soup = BeautifulSoup(html.text, 'lxml')

        name = soup.select_one('#gsc_prf_in').text
        affiliation = soup.select_one('#gsc_prf_in+ .gsc_prf_il').text

        try:
            email = soup.select_one('#gsc_prf_ivh').text
        except:
            email = None

        try:
            interests = soup.select_one('#gsc_prf_int').text
        except:
            interests = None

        for cited_by_public_access in soup.select('.gsc_rsb'):
            citations_all = cited_by_public_access.select_one('tr:nth-child(1) .gsc_rsb_sc1+ .gsc_rsb_std').text
            citations_since2017 = cited_by_public_access.select_one('tr:nth-child(1) .gsc_rsb_std+ .gsc_rsb_std').text
            h_index_all = cited_by_public_access.select_one('tr:nth-child(2) .gsc_rsb_sc1+ .gsc_rsb_std').text
            i10_index_all = cited_by_public_access.select_one('tr~ tr+ tr .gsc_rsb_sc1+ .gsc_rsb_std').text
            i10_index_2017 = cited_by_public_access.select_one('tr~ tr+ tr .gsc_rsb_std+ .gsc_rsb_std').text
            print(f'Nombre: {name}-----Indice  H:{h_index_all}--Citations : {citations_all}')
            dict_frame["profiles"].append({"name":name,"Index_H":h_index_all,"citations":citations_all,
            "citations_since2017":citations_since2017,"Index_i10":i10_index_all,"Index_i10_since2017":i10_index_2017})
    write_results(dict_frame)



     
        
##Description: Metodo para obtener id de perfiles
#Params: url(Url sitio web de busqueda) , dict(Lista vacia para almacenar los ids)
#return : profiles(url,dict) try , author(dict) except
def get_id_profiles(url,dict):
    try:
        #Setting search 
        headers = {
        'User-agent':
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }

        proxies = {
    'http': os.getenv('HTTP_PROXY')
        }

        html = requests.get(url, headers=headers, proxies=proxies).text
        soup =BeautifulSoup(html,'lxml')
        
        for result in soup.select('.gs_ai_chpr'):
            name = result.select_one('.gs_ai_name a').text
            link = result.select_one('.gs_ai_name a')['href']
            id = link
            id_identifer = 'user='
            before_keyword, keyword, after_keyword = id.partition(id_identifer)
            author_id = after_keyword
            affiliations = result.select_one('.gs_ai_aff').text
            email = result.select_one('.gs_ai_eml').text
            try:
                interests = result.select_one('.gs_ai_one_int').text
            except:
                interests = None
            # "Cited by 107390" = getting text string -> splitting by a space -> ['Cited', 'by', '21180'] and taking [2] index which is the number.
            cited_by = result.select_one('.gs_ai_cby').text.split(' ')[2] 
            dict.append(author_id)
        
        #after button text
        buttons=soup.select('.gsc_pgn button')
        afterButton=buttons[1]['onclick']
        string='after_author'
        a,b,c=afterButton.partition(string)
      
        #cutting string 
        index_c=c.index('d')
        index_h=c.index('x')
        subString=c[4:16]
        
        get_id_profiles(url+'&after_author='+subString,dict)
    except:
        get_inf_author(dict)

emptydict=[]
get_id_profiles(search_link+search_word,emptydict)
