*pyobs-launcher*
================

This is a launcher with graphical user interface for *pyobs* configurations, which
can mainly be used in a Windows environment as an alternative to *pyobsd*.

A configuraton file (default: config.yaml) is required of the following form:

    python: /path/to/python
    pyobs: /pyth/to/pyobs
    configs:
      - /path/to/config_to_start.yaml
      - /path/to/another_config_to_start.yaml
