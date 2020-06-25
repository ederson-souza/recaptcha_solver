# SCREEN RESOLUTION MUST BE 1920X1080

import os
import random
from time import sleep

import cv2
import torch
import torchvision
from numpy.random import randint
from numpy import where
from PIL import Image
from selenium.webdriver import Firefox
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


import detectron2
from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog
from detectron2.engine import DefaultPredictor
from detectron2.utils.logger import setup_logger

setup_logger()

def detectron_init():
 
    """ Description: Detetron2 configuration and initialization.
    :raises:
    Model 
    :rtype:
    Model
    """
    cfg= get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.2  # set threshold for this model
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
    cfg.MODEL.DEVICE = 'cpu'
    predictor = DefaultPredictor(cfg)
    return predictor

def webdriver_init(path):

    """ Webdriver inicialization
    :type path: string
    :param path: path to webdriver file 
    
    :raises:
    webdriver loaded
    :rtype:
    webdriver
    """

    driver = Firefox(path)
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

def predictions(predictor, image):
    outputs = predictor(image)
    fire_hydrant = outputs['instances'].pred_classes.to('cpu').numpy()
    indexes = where(fire_hydrant == 10)[0]
    predictions = []
    for index in indexes:
        predictions.append(list(outputs['instances'][index:index + 1].pred_boxes.tensor.numpy()[0]))

    return predictions

def find_and_click():
    """ Description
    - Make Predictions
    - Find object center
    - Click on the object
    """
    image = cv2.imread('image.png')
    for eachObject in predictions(predictor, image):
        x = (eachObject[0] + eachObject[2])/2
        y = (eachObject[1] + eachObject[3])/2

        actions = ActionChains(driver)
        actions.move_to_element_with_offset(quadro, x + randint(5,20), y + randint(5,20)).click().perform()
        sleep(randint(1,2))

def image_click(predictor, image, objeto):
    matrix = {
            11: None, 12: None, 13: None, 
            21: None, 22: None, 23: None, 
            31: None, 32: None, 33: None
            }

    for eachObject in predictions(predictor, image, objeto):
        x = (eachObject[0] + eachObject[2])/2
        y = (eachObject[1] + eachObject[3])/2
        if x <= 130:
            if y <= 130:
                matrix[11] = [x,y]
            elif y <= 260:
                matrix[21] = [x,y]
            else:
                matrix[31] = [x,y]
        elif x <= 260:
            if y <= 130:
                matrix[12] = [x,y]
            elif y <= 260:
                matrix[22] = [x,y]
            else:
                matrix[32] = [x,y]
        else:
            if y <= 130:
                matrix[13] = [x,y]
            elif y <= 260:
                matrix[23] = [x,y]
            else:
                matrix[33] = [x,y]

    for n in matrix:
        if matrix[n] != None:
            actions = ActionChains(driver)
            actions.move_to_element_with_offset(quadro, matrix[n][0] + randint(5,20), matrix[n][1]  + randint(5,20)).click().perform()
            sleep(randint(1,2))


predictor = detectron_init()

PATH = "C:\\Users\\eders\\Projects\\reCaptcha\\geckodriver.exe"
WEBSITE = "https://projudi.tjpr.jus.br/projudi_consulta/processo/consultaPublicaProcessosPronunciamentosJudiciais.do?actionType=iniciar"

#Inicialização da navegação
driver = webdriver_init(PATH)
driver.get(WEBSITE)


#Filtros drop-down
element = driver.find_element_by_xpath("/html/body/div[1]/div[1]/form/fieldset/table[1]/tbody/tr[4]/td[2]/select")
element.find_elements_by_tag_name("option")[154].click()
sleep(0.5)
element = driver.find_element_by_xpath('/html/body/div[1]/div[1]/form/fieldset/table[1]/tbody/tr[5]/td[2]/select')
element.find_elements_by_tag_name("option")[9].click()
sleep(0.5)
element = driver.find_element_by_xpath('/html/body/div[1]/div[1]/form/fieldset/table[1]/tbody/tr[7]/td[2]/select')
element.find_elements_by_tag_name("option")[2].click()
sleep(2)


#click no quadrado Eu não sou robô
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


objective = driver.find_element_by_xpath('/html/body/div/div/div[2]/div[1]/div[1]/div/strong').text #texto do objeto a ser identificado
counter = 0
while objective != 'um hidrante':  
    actions = ActionChains(driver)
    element = driver.find_element_by_xpath('/html/body/div/div/div[3]/div[2]/div[1]/div[1]/div[1]/button')
    actions.move_to_element_with_offset(element, randint(0,5), randint(0,4)).click().perform()
    sleep(randint(1,3))
    objective = driver.find_element_by_xpath('/html/body/div/div/div[2]/div[1]/div[1]/div/strong').text
    counter +=1
    if counter == 10:
        driver.close()


#preprocessamento da imagem
image_preprocessing()

#localização do quadro da imagem
quadro = driver.find_element_by_xpath('/html/body/div/div')

#clica nos objetos localizados
find_and_click()

#espera por novas fotos
sleep(6)

#preprocessamento da imagem
image_preprocessing()

#clica nos objetos localizados
find_and_click()
        
#localiza o botão enviar e clica
actions = ActionChains(driver)
element = driver.find_element_by_xpath('/html/body/div/div/div[3]/div[2]/div[1]/div[2]')
sleep(randint(3,5))
actions.move_to_element_with_offset(quadro, randint(370,380), randint(550,570)).double_click().perform()
print('END') 
