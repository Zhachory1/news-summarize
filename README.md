# news-summarize
Quick news summarize to take in a url and output some information on a webpage.

I build this app using bazel: https://bazel.build/install

To run the test application, run the following command and go to the link given:

```
$ alias please="bazel"
$ please run src:wsgi
```

## Docker

```bash
docker build -f dockerfile -t news-summarize .
docker run --rm -p 8080:8080 news-summarize
```

## Tests

```bash
python -m unittest discover -s tests
```

## Notes

- Article extraction is cached by normalized URL, so tracking query params/fragments do not trigger duplicate downloads.
- Runtime dependencies in `third_party/requirements.txt` use compatibility ranges instead of stale exact pins.
