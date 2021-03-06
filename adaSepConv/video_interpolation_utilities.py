import math, re, os
import tensorflow as tf
import numpy as np
from matplotlib import pyplot as plt
from tensorflow.keras.models import model_from_json
import cv2
from matplotlib import pyplot as plt

def capture_frames_from_video(videofile):
    
      vidcap = cv2.VideoCapture(videofile)
      success,image = vidcap.read()
      count = 0
      file_name  = os.path.basename(os.path.splitext(videofile)[0])
      if not os.path.isdir("./frames_"+ file_name):
          os.mkdir("./frames_"+ file_name)
          while success:

              cv2.imwrite("./frames_%s/%s.jpg" % (file_name,str(count).zfill(6)), image)     # save frame as JPEG file      
              success,image = vidcap.read()
              # print('Read a new frame: ', success)
              count += 2
      return vidcap.get(cv2.CAP_PROP_FPS)



def pad_frame(image,pad_h,pad_w):
    return np.pad(image, ((0,0),(pad_h//2,pad_h//2 if pad_h%2 == 0 else pad_h//2 + 1),(pad_w//2,pad_w//2 if pad_w%2 == 0 else pad_w//2 +1),(0,0)), 'constant')


def interpolate_frame(img,loaded_model,batch=16,pred_h=128,pred_w=128):
    # img = np.concatenate((pad_frame(image1,36),pad_frame(image3,36)),axis = -1)
#     img = np.expand_dims(img, axis=0)/255.
    # print(img.shape)
    pad_h = int((1-(img.shape[1]/pred_h-img.shape[1]//pred_h))*pred_h) if img.shape[1]%pred_w!=0 else 0
    pad_w = int((1-(img.shape[2]/pred_w-img.shape[2]//pred_w))*pred_w) if img.shape[2]%pred_w!=0 else 0
    img = pad_frame(img,int(pad_h),int(pad_w))
    interpolated_image = np.zeros((1,img.shape[1],img.shape[2],3))
    img = img/255.
    for row in range(img.shape[1]//pred_h):
        for col in range(img.shape[2]//pred_w):
            interpolated_image[:,row*pred_h:row*pred_h+pred_h,col*pred_w:col*pred_w+pred_w,:] = loaded_model.predict(img[:,row*pred_h:row*pred_h+pred_h,col*pred_w:col*pred_w+pred_w,:],batch_size = batch,use_multiprocessing = True)
    return interpolated_image



def create_interpolated_frames(video_frames_filepath,loaded_model,batch,video_filename):
  batch_of_images = []
  batch_size = 0
  count = 0
  interpolated_filenumber = 1
  video_frames_filepath = sorted(video_frames_filepath)
  for i in range(len(video_frames_filepath)-1):
    image1_path = video_frames_filepath[i]
    image2_path = video_frames_filepath[i+1]
    image1 = cv2.imread(image1_path)
    image2 = cv2.imread(image2_path)
    img = np.concatenate([image1,image2],axis = -1)
    img = np.expand_dims(img,axis = 0)
    height = img.shape[1]
    width = img.shape[2]
    if batch_size < batch-1:
      if type(batch_of_images) == list:
        batch_of_images = img 
        batch_size += 1
      else:
        batch_of_images = np.concatenate([batch_of_images,img],axis = 0)
        batch_size += 1
      continue
    else :
      if type(batch_of_images) == list:
        batch_of_images = img 
        batch_size += 1
      else:
        batch_of_images =  np.concatenate([img],axis = 0) if type(batch_of_images)==list else np.concatenate([batch_of_images,img])
        batch_size += 1
      interpolated_images = interpolate_frame(batch_of_images,loaded_model,batch)
      for j in range(batch):
        image_name = './frames_'+ video_filename+'/'+str(interpolated_filenumber).zfill(6)+'.jpg'
        cv2.imwrite(image_name,interpolated_images[j,:,:,:]*255.)
        cut_extra(image_name,height,width)
        interpolated_filenumber += 2
      batch_size = 0
      batch_of_images = []
      count += batch
      print("interpolated %d frames" %(count))



def cut_extra_video(video_frames_list,height,width):
  x = 1
  for frame in video_frames_list:
    file_name  = os.path.basename(os.path.splitext(frame)[0])
    current_file_to_cut = str(x).zfill(6)
    if(current_file_to_cut==file_name):
      img = cv2.imread(frame)
      img = img[(img.shape[0]-height)/2:height+(img.shape[0]-height)/2,(img.shape[1]-width)/2:width+(img.shape[1]-width)/2,:]
      cv2.imwrite(frame,img)
      x += 2

def cut_extra(video_frame,height,width):
  img = cv2.imread(video_frame)
  img = img[int((img.shape[0]-height)/2):height+int((img.shape[0]-height)/2),int((img.shape[1]-width)/2):width+int((img.shape[1]-width)/2),:]
  cv2.imwrite(video_frame,img)


def convert_frames_to_video(list_of_files,pathOut,fps):

    frame_array = []
    for i in range(len(list_of_files)):
        # filename=pathIn + files[i]
        #reading each files
        img = cv2.imread(list_of_files[i])
        height, width, layers = img.shape
        size = (width,height)
        print(list_of_files[i])
        #inserting the frames into an image array
        frame_array.append(img)

    out = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'DIVX'), fps, size)

    for i in range(len(frame_array)):
        # writing to a image array
        out.write(frame_array[i])
    out.release()


