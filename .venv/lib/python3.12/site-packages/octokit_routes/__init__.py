import json
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_webhook_names():
    webhooks = _load_json(os.path.join(__location__, "webhooks", "index.json"))
    webhook_names = ["*"]
    webhook_names += [m["name"] + ".{}".format(n) for m in webhooks for n in m["actions"]]
    webhook_names += [m["name"] for m in webhooks if m["actions"] == []]
    return webhook_names


def _load_spec(spec_name):
    return _load_json(os.path.join(__location__, "routes", spec_name))


def _list_specs():
    return [
        d.name for d in os.scandir(os.path.join(__location__, "routes")) if d.is_file() and not d.name.endswith("js")
    ]


specs = _list_specs()
specifications = {spec.replace(".json", ""): _load_spec(spec) for spec in specs}

webhook_names = _load_webhook_names()
