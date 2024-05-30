import cv2
import os
import time

dataset_dir = 'dataset'

def count_files(folder_path):
    return len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def collect_data(person_name, interval=0.5):
    person_dir = os.path.join(dataset_dir, person_name)
    create_directory(person_dir)
    cap = cv2.VideoCapture(1)
    count = count_files(person_dir)
    start_time = time.time()
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            flipped_frame = cv2.flip(frame, 1)
            cv2.imshow('Webcam', flipped_frame)
            if time.time() - start_time >= interval:
                img_name = os.path.join(person_dir, f'{person_name}_{count}.jpg')
                cv2.imwrite(img_name, frame)
                print(f'{img_name} saved!')
                count += 1
                start_time = time.time()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

person_name = input('Enter the name of the person: ')
interval = int(input('Enter the interval between captures (in seconds): '))
collect_data(person_name, interval)
