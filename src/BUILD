load("@rules_python//python:defs.bzl", "py_binary")
load("@my_deps//:requirements.bzl", "requirement")
load("@io_bazel_rules_docker//container:container.bzl", "container_push")
load("@io_bazel_rules_docker//python3:image.bzl", py_image="py3_image")


package(default_visibility = ["//visibility:public"])

py_library(
    name = "news_summarize",
    srcs = glob(["**/*.py"]),
    deps = [
        requirement("flask"),
        requirement("nltk"),
        requirement("textblob"),
        requirement("newspaper3k"),
        requirement("absl-py"),
    ],
)

py_binary(
    name = "wsgi",
    srcs = ["wsgi.py"],
    data = [
        "//src/static:favicon.ico",
        "//src/static:loading-gif.gif",
        "//src/templates:index.html",
    ],
    deps = [
        ":news_summarize",   
    ]
)

py_image(
    name = "news_summarize_image",
    srcs = ["wsgi.py"],
    data = [
        "//src/static:favicon.ico",
        "//src/static:loading-gif.gif",
        "//src/templates:index.html",
    ],
    deps = [
        ":news_summarize",   
    ],
    main = "wsgi.py"
)

container_push(
    name = "news_summarize-push",
    format = "Docker",
    image = ":news_summarize_image",
    registry = "index.docker.io",
    repository = "zhachory1/news-summarize",
)