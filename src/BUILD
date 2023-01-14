load("@rules_python//python:defs.bzl", "py_binary")
load("@my_deps//:requirements.bzl", "requirement")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "news_summarize",
    srcs = glob(["**/*.py"]),
    deps = [
        requirement("flask"),
        requirement("nltk"),
        requirement("textblob"),
        requirement("newspaper3k"),
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