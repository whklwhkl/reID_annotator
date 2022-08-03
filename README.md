# reID_annotator
this repository contains a simple web application for re-id annotation

## Prerequisites
`Python==3.7.6`\
`Pillow==8.0.1`\
`Flask==1.1.1`

## Data Preparation

- A `IMAGE_FOLDER` is organized like the following example
```
IMAGE_FOLDER
|--LABEL1
    |--IMAGE1.jpg
    |--IMAGE2.jpg
|--LABEL2
    |--IMAGE3.jpg
    |--IMAGE4.jpg
```

- [optional] A `WORK_LIST` is a `json` file that holds the list of pairs of labels in the following manner
```
[
  ["LABEL1", "LABEL2"],
  ["LABEL3", "LABEL4"]
]
```

**NOTE**: the `WORK_LIST` should be sorted in ascending order of priority

## Launch
```bash
python app.py ${IMAGE_FOLDER} [-o ${WORK_LIST.json}]
```
This should prompt you a HTTP link that users can access. For example `http://localhost`

## Work flow
1. go to the home page `http://${HOST_IP}`
2. then enter a user name and `login` if it's the first time
3. select `yes` or `no` repeatedly until the annotation is finished
4. once done, a summary page will show up and you can download the annotations in `json`

## Data persistence
### save
```bash
curl http://${HOST_IP}/download > backup.json
```
### load
```bash
curl -F "record=@backup.json" http://${HOST_IP}/upload
```

<!-- ## Coming soon -->
