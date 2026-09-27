# [H] vLLM vulnerable to remote code execution via transformers_utils/get_config

## Summary
Severity: High
Advisory: GHSA-8fr4-5q9j-m8gm
CVE: CVE-2025-66448
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-8fr4-5q9j-m8gm
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0 <0.11.1

## Details
### Summary

`vllm` has a critical remote code execution vector in a config class named `Nemotron_Nano_VL_Config`. When `vllm` loads a model config that contains an `auto_map` entry, the config class resolves that mapping with `get_class_from_dynamic_module(...)` and immediately instantiates the returned class. This fetches and executes Python from the remote repository referenced in the `auto_map` string. Crucially, this happens even when the caller explicitly sets `trust_remote_code=False` in `vllm.transformers_utils.config.get_config`. In practice, an attacker can publish a benign-looking frontend repo whose `config.json` points via `auto_map` to a separate malicious backend repo; loading the frontend will silently run the backend’s code on the victim host.

### Details

The vulnerable code resolves and instantiates classes from `auto_map` entries without checking whether those entries point to a different repo or whether remote code execution is allowed.

```python
class Nemotron_Nano_VL_Config(PretrainedConfig):
    model_type = 'Llama_Nemotron_Nano_VL'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if vision_config is not None:
            assert "auto_map" in vision_config and "AutoConfig" in vision_config["auto_map"]
            # <-- vulnerable dynamic resolution + instantiation happens here
            vision_auto_config = get_class_from_dynamic_module(*vision_config["auto_map"]["AutoConfig"].split("--")[::-1])
            self.vision_config = vision_auto_config(**vision_config)
        else:
            self.vision_config = PretrainedConfig()
```

`get_class_from_dynamic_module(...)` is capable of fetching and importing code from the Hugging Face repo specified in the mapping. `trust_remote_code` is not enforced for this code path. As a result, a frontend repo can redirect the loader to any backend repo and cause code execution, bypassing the `trust_remote_code` guard.

### Impact

This is a critical vulnerability because it breaks the documented `trust_remote_code` safety boundary in a core model-loading utility. The vulnerable code lives in a common loading path, so any application, service, CI job, or developer machine that uses `vllm`’s transformer utilities to load configs can be affected. The attack requires only two repos and no user interaction beyond loading the frontend model. A successful exploit can execute arbitrary commands on the host.

### Fixes

* https://github.com/vllm-project/vllm/pull/28126

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-8fr4-5q9j-m8gm
- https://nvd.nist.gov/vuln/detail/CVE-2025-66448
- https://github.com/vllm-project/vllm/pull/28126
- https://github.com/vllm-project/vllm/commit/ffb08379d8870a1a81ba82b72797f196838d0c86
- https://github.com/advisories/GHSA-8fr4-5q9j-m8gm
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-2015.yaml
- https://github.com/vllm-project/vllm
- https://pypi.org/project/vllm
