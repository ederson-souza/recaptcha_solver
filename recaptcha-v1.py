# SCREEN RESOLUTION MUST BE 1920X1080
# coding: UTF-8

import os
from time import sleep

import tensorflow as tf
from imageai.Detection import ObjectDetection
from numpy.random import randint
from numpy import zeros
from PIL import Image
from selenium.webdriver import Chrome
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

def webdriver_init(path):

    """ Webdriver inicialization
    :type path: string
    :param path: path to webdriver file 
    
    :raises:
    webdriver loaded
    :rtype:
    webdriver
    """

    driver = Chrome(path)
    return driver

def crop_image():
    
    """ Description: Load screenshot, crop and save it.
    :raises:
    reCaptcha croped image to make predictions
    :rtype:
    image.png
    """
    x_loc = 175
    y_loc = 10
    width = x_loc + 400
    height = y_loc + 582
    im = Image.open('images/pageImage.png')
    im = im.crop((int(x_loc), int(y_loc), int(width), int(height)))
    im.save('images/image.png')

def predictions():
    
    """ Description: 
    Object detection using Tensorflow and Resnet50.
    :raises:
    Predicted Objects
    :rtype:
    Dictionary
    """
    execution_path = os.getcwd()
    detector = ObjectDetection()
    detector.setModelTypeAsRetinaNet()
    detector.setModelPath(os.path.join(execution_path , "resnet50_coco_best_v2.0.1.h5"))
    detector.loadModel()
    custom_objects = detector.CustomObjects(
                                            bicycle=bicycle, 
                                            fire_hydrant=fire_hydrant
                                            )
    detections = detector.detectCustomObjectsFromImage(
                                                       custom_objects = custom_objects, 
                                                       thread_safe = True, 
                                                       minimum_percentage_probability=30, 
                                                       input_image=os.path.join(execution_path , "images/image.png"), 
                                                       output_image_path=os.path.join(execution_path , "images/imagenew.png")
                                                       )
    return detections

def image_preprocessing():
   
    """ 
    Description: Image preprocessing pipeline.
    - Switch to root content
    - Take Screenshot
    - Crop Image
    - Back to iFrame
    """   
   
    #troca entre iframe e conteúdo raiz
    driver.switch_to.default_content()

    #screenshot da tela
    driver.save_screenshot("images/pageImage.png")

    #recorte da imagem
    crop_image()

    #retorno ao iframe do recaptcha
    driver.switch_to.frame(name)

def image_click():

    """ Description
    - Make Predictions
    - Find object center
    - Click on the object
    """

    matrix = zeros((3,3),dtype=object)

    for eachObject in predictions():
        x = (eachObject["box_points"][0] + eachObject["box_points"][2])/2
        y = (eachObject["box_points"][1] + eachObject["box_points"][3])/2
        if x <= 130:
            if y <= 130:
                matrix[0,0] = [x,y]
            elif y <= 260:
                matrix[1,0] = [x,y]
            else:
                matrix[2,0] = [x,y]
        elif x <= 260:
            if y <= 130:
                matrix[0,1] = [x,y]
            elif y <= 260:
                matrix[1,1] = [x,y]
            else:
                matrix[2,1] = [x,y]
        else:
            if y <= 130:
                matrix[0,2] = [x,y]
            elif y <= 260:
                matrix[1,2] = [x,y]
            else:
                matrix[2,2] = [x,y]

    for r in range(3):
        for c in range(3):
            if matrix[r,c] != 0:
                actions = ActionChains(driver)
                actions.move_to_element_with_offset(quadro, matrix[r,c][0] + randint(5,20), matrix[r,c][1]  + randint(5,20)).click().perform()
                sleep(randint(1,2))


PATH = "C:\\Users\\eders\\Projects\\reCaptcha\\webdrivers\\chromedriver.exe"
WEBSITE = "https://projudi.tjpr.jus.br/projudi_consulta/processo/consultaPublicaProcessosPronunciamentosJudiciais.do?actionType=iniciar"

#Inicialização da navegação
driver = webdriver_init(PATH)
driver.get(WEBSITE)

#Filtros drop-down
element = driver.find_element_by_xpath("/html/body/div[1]/div[1]/form/fieldset/table[1]/tbody/tr[4]/td[2]/select")
element.find_elements_by_tag_name("option")[154].click()
sleep(0.5)
element = driver.find_element_by_xpath('/html/body/div[1]/div[1]/form/fieldset/table[1]/tbody/tr[5]/td[2]/select')
element.find_elements_by_tag_name("option")[11].click()
sleep(0.5)
element = driver.find_element_by_xpath('/html/body/div[1]/div[1]/form/fieldset/table[1]/tbody/tr[7]/td[2]/select')
element.find_elements_by_tag_name("option")[2].click()
sleep(2)


#click no quadrado 'Eu não sou robô'
frames = driver.find_elements_by_tag_name("iframe")
frame = frames[0]
name = frame.get_attribute('name')
driver.switch_to.frame(name)
element = driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[1]/div')
actions = ActionChains(driver)
actions.move_to_element_with_offset(element,randint(2,6), randint(3,8)).click().perform()
sleep(3)

#troca para o frame das imagens
driver.switch_to.default_content()
frame = frames[2]
name = frame.get_attribute('name')
driver.switch_to.frame(name)

#texto do objeto a ser identificado
objective = driver.find_element_by_xpath('/html/body/div/div/div[2]/div[1]/div[1]/div/strong').text 

#busca por images 'um hidrante' ou 'bicicletas'
counter = 0
while objective != 'um hidrante':# and objective != 'bicicletas':  
    actions = ActionChains(driver)
    element = driver.find_element_by_xpath('/html/body/div/div/div[3]/div[2]/div[1]/div[2]/button')
    actions.move_to_element_with_offset(element, randint(10,30), randint(5,10)).perform()    
    actions = ActionChains(driver)
    element = driver.find_element_by_xpath('/html/body/div/div/div[3]/div[2]/div[1]/div[1]/div[1]/button')
    actions.move_to_element_with_offset(element, randint(0,5), randint(0,4)).click().perform()
    sleep(randint(1,3))
    objective = driver.find_element_by_xpath('/html/body/div/div/div[2]/div[1]/div[1]/div/strong').text
    counter +=1
    if counter == 10:
        driver.close()

bicycle = False
fire_hydrant = False
if objective == 'bicicletas':
    bicycle = True
elif objective == 'um hidrante':
    fire_hydrant = True

#preprocessamento da imagem
image_preprocessing()

#localização do quadro da imagem
quadro = driver.find_element_by_xpath('/html/body/div/div')

#clica nos objetos localizados
image_click()

#espera por novas fotos
sleep(6)

#preprocessamento da imagem
image_preprocessing()

#clica nos objetos localizados
image_click()
        
#localiza o botão enviar e clica
actions = ActionChains(driver)
element = driver.find_element_by_xpath('/html/body/div/div/div[3]/div[2]/div[1]/div[2]')
sleep(randint(3,5))
actions.move_to_element_with_offset(quadro, randint(370,380), randint(550,570)).double_click().perform()
print('END')    
