![logo](assets/logo.png)
# ShowData: Show your dataset in web browser!

ShowData is a python tool to visualize and manage the multi-media files in remote server. 
It provides useful commond-line tools and fully customizeble API to generate html file for multi-media files.

## Examples
It supports filtering data by text, sorting data by coloum values and pagination. 

VeRiWild dataset
![example](assets/example1.png)
![example](assets/example2.png)

ReID Strong baseline Results  
![example](assets/example3.png)

## Install 

```
pip install -U git+https://github.com/silverbulletmdc/showdata
```

## Command Line Tools

### Basic usage
Open a file server (a stronger alternative to `python -m http.server`)
``` 
showdata server -p <port, default 8000> -h <host, default 0.0.0.0>
```

Compare images with the same name from different folders 
```
showdata compare <path-a> <path-b> <path-c> -o <output-path>
```

All string values ends with `png`/`jpg`/`jpeg` will be rendered as images， `mp4` will be rendered as video. Others are rendered as text.

## API
```python
from showdata import generate_html_table
data = [
    {
        "idx": 1,
        "label": 'cat',
        "img": {
            "src": "images/cat.jpg",
            "text": "The text will be shown on the top of the image",
            "style": "border: 2mm solid green"
        }
        "mask": 'images/cat_mask.png',
    },
    {
        "idx": 2,
        "label": 'dog',
        "img": 'images/dog.jpg',
        "mask": 'images/dog_mask.png',
    },
]
generate_html_table(data, output_path='index.html')
```
