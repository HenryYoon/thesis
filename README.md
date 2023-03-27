This repository (repo) contains source code for [KIICE paper of mine](https://www.dbpia.co.kr/Journal/articleDetail?nodeId=NODE10608071).

In this paper, we present Transformer-based fact checking model which improves computational efficiency. Locality Sensitive Hashing (LSH) is employed to efficiently compute attention value so that it can reduce the computation time. With LSH, model can group semantically similar words, and compute attention value within the group. The performance of proposed model is 75% for accuracy, 42.9% and 75% for Fl micro score and F1 macro score, respectively.

As a result, we awarded best paper in 2021 KIICE spring conference.

## Usage
Our code is written in Windows device. Please be aware of that.

First, you need to install required libraries with this command:

```python
pip install -r requirements.txt
```

If you want to run our code, please input this command

```
python ./src/experiment.py
```

## Tech Stack

* Data: Pandas, Numpy, Scikit-learn, Requests, BeautifulSoup
* Visualization: Plotly, Matplotlib
* ML: Gensim, SciPy

## License

[GNU GENERAL PUBLIC](LICENSE) © Hee Seung Yun