# image-labeler
Image labeling tool in pure HTML5. Useful for building image classification datasets.

- No annotations
- No bounding boxes
- No fancy frontend technologies
- It works blazingly fast and is very convenient
- More than one label is possible
- 100% controllable with keyboard, no mouse gestures are required

## How to run

```
python3 app.py --images=/path/to/images/directory --labels=/path/to/labels.txt
```

`labels.txt` is one line per label, name and description separated by `#`.

The labels are written to `/path/to/images/directory/json`.

## Installation

```
pip3 install flask
```
