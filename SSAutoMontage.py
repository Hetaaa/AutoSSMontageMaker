import speech_recognition as sr
import os
from moviepy.editor import *
import math
import random

fullfight = 0
subclip_lenght = 7


def sortSS(val):
    return val[-4]

#get all files from directory
vidList = [f for f in os.listdir(os.path.join(os.getcwd(),"videos")) if os.path.isfile(os.path.join(os.path.join(os.getcwd(),"videos"), f))]

#get audio directories


#list for words to indicate fight
wordsToChceck =["3, 2, 1", "5, 4, 3", "4, 3, 2", "five, four", "four, three", "three, two", "two, one", "5-4", "4-3", "3-2", "2-1", "five four", "four three", "three two", "two one"]


FightStartTimer = 0
FightEndTimer = 0
FightStartIndicator = 0
finalVidCuts = []

r = sr.Recognizer()


#for evety file in directory
for x in range(len(vidList)):
    #get file name
    fullVidParth = os.path.join(os.path.join(os.getcwd(),"videos",vidList[x]))
    currentClip = VideoFileClip(fullVidParth)
    #get file duration
    currentClip_lenght = currentClip.duration
    

    #cut whole file into 20s subclips
    for y in range(math.floor(currentClip_lenght/subclip_lenght)):
        #cut
        currentSubClip = currentClip.subclip(y*subclip_lenght, y*subclip_lenght+subclip_lenght)

        #name file
        filename = "temp_audio_subclip"+str(x)+str(f"{y:03}")+".wav"
        currentSubClip.audio.write_audiofile(os.path.join(os.getcwd(),"temp","audio",filename),codec='pcm_s16le')



    #get all clips from directory
    tempAudioList = [f for f in os.listdir(os.path.join(os.getcwd(),"temp","audio")) if os.path.isfile(os.path.join(os.path.join(os.getcwd(),"temp","audio"), f))]
    tempAudioList.sort(key=sortSS)
    # get the subclip
    for z in range(len(tempAudioList)):
        fullAudioPath = os.path.join(os.path.join(os.getcwd(),"temp","audio",tempAudioList[z]))
        with sr.AudioFile(fullAudioPath) as source:
            audio = r.record(source)

        print('Analyzing Audio from video '+ str(x) + ' subclip ' + str(z))
        #analyze audio
        try:
            text = r.recognize_whisper(audio, language="english")
        except sr.UnknownValueError:
            print("Sphinx could not understand audio")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))
        #look for word in clip
        if any(word in text for word in wordsToChceck):
            print("Found Engage")
            print(text)
            # if full fight option is enabled mark start and end of the fight
            if fullfight == 1:
                FightEndTimer = z*subclip_lenght
                if FightStartIndicator == 0:
                   FightStartTimer = z*subclip_lenght
                   FightStartIndicator = 1
            # if full fight option is disbanled get only the subclip with engage
            if fullfight == 0:
                cutClip = currentClip.subclip(z*subclip_lenght+math.floor((subclip_lenght/4)),((z+1)*subclip_lenght)+3).fx(vfx.fadein, 0.3).fx(vfx.fadeout, 0.3)
                finalVidCuts.append(cutClip)       
        
 
    #remove temp audio subclips
    dir = os.path.join(os.getcwd(),"temp","audio")
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))


    print(FightStartTimer)
    print(FightEndTimer)

    
    # if fullfight is enabled cut the fight part from video using marks
    if fullfight == 1:
        cutClip = currentClip.subclip(FightStartTimer,FightEndTimer).fx(vfx.fadein, 0.3).fx(vfx.fadeout, 0.3)
        cutClip.audio = cutClip.audio.fx(afx.audio_fadein, 0.3).fx(afx.audio_fadeout, 0.3)
        finalVidCuts.append(cutClip)
        FightStartTimer = 0
        FightEndTimer = 0

#export video        
outputDirectory = os.path.join(os.getcwd(),"output","montage.mp4")



#merge all viedo clips
finalClip = concatenate_videoclips(finalVidCuts)
finalClipLenght = finalClip.duration
currentAudioDuration = 0
audioCounter = 0

#get all music files from directory
audioList = [a for a in os.listdir(os.path.join(os.getcwd(),"music")) if os.path.isfile(os.path.join(os.path.join(os.getcwd(),"music"), a))]
#randomize
random.shuffle(audioList)

finalAudioList = []

#add music files to list when total duration of music is lower then total duration of video
while finalClipLenght > currentAudioDuration:
    if audioCounter == len(audioList):
        #loop the counter
        audioCounter = 0

    fullFinalAudioPath = os.path.join(os.path.join(os.getcwd(),"music",audioList[audioCounter]))
    audioClip = AudioFileClip(fullFinalAudioPath).fx(afx.audio_fadein, 0.3).fx(afx.audio_fadeout, 0.3)
    #add time to duration counter
    currentAudioDuration = currentAudioDuration + audioClip.duration
    audioCounter =  audioCounter + 1

    #if total music is greater then cut the last part
    if finalClipLenght < currentAudioDuration:
        audioClip = audioClip.subclip(0,audioClip.duration-(currentAudioDuration-finalClipLenght)).fx(afx.audio_fadeout, 2)
       
    finalAudioList.append(audioClip)

#merge all music    
finalAudioClip = concatenate_audioclips(finalAudioList)
#merge the original sound with music
CombinedfinalAudioClip = CompositeAudioClip([finalClip.audio, finalAudioClip])
finalClip.audio = CombinedfinalAudioClip

finalClip.write_videofile(outputDirectory, codec='libx264', fps=30, bitrate='5000000')







  








