import speech_recognition as sr
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx, AudioFileClip, afx
import math

def sortSS(val):
    return val[-4]

#get all files from directory
vidList = [f for f in os.listdir(os.path.join(os.getcwd(),"videos")) if os.path.isfile(os.path.join(os.path.join(os.getcwd(),"videos"), f))]

#get audio directories


#list for words to indicate fight
wordsToChceck =["3, 2, 1", "5, 4, 3", "4, 3, 2", "five, four", "four, three", "three, two", "two, one", "5-4", "4-3", "3-2", "2-1", "five four", "four three", "three two", "two one"]

subclip_lenght = 20
FightStartTimerList = []
FightEndTimerList = []
FightStartIndicator = 0

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



    # get the subclip
    tempAudioList = [f for f in os.listdir(os.path.join(os.getcwd(),"temp","audio")) if os.path.isfile(os.path.join(os.path.join(os.getcwd(),"temp","audio"), f))]
    tempAudioList.sort(key=sortSS)
    for z in range(len(tempAudioList)):
        fullAudioPath = os.path.join(os.path.join(os.getcwd(),"temp","audio",tempAudioList[z]))
        with sr.AudioFile(fullAudioPath) as source:
            audio = r.record(source)

        print('Analyzing Audio from video '+ str(x) + ' subclip ' + str(z))
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
            FightEndTimer = z*20
            if FightStartIndicator == 0:
                FightStartTimerList.append(z*20)
                FightStartIndicator = 1
        
    FightEndTimerList.append(FightEndTimer)

    
    #remove temp audio subclips
    dir = os.path.join(os.getcwd(),"temp","audio")
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))


    print(FightStartTimerList)
    print(FightEndTimerList)
    final = currentClip.subclip(FightStartTimerList[0],FightEndTimerList[0])
    outputDirectory = os.path.join(os.getcwd(),"output","montage.mp4")
    final.write_videofile(outputDirectory)







  








