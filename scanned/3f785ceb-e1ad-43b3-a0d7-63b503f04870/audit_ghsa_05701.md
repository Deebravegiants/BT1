# [H] vLLM affected by RCE via auto_map dynamic module loading during model initialization

## Summary
Severity: High
Advisory: GHSA-2pc9-4j83-qjmr
CVE: CVE-2026-22807
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-2pc9-4j83-qjmr
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.10.1 <0.14.0

## Details
# Summary

vLLM loads Hugging Face `auto_map` dynamic modules during model resolution **without gating on `trust_remote_code`**, allowing attacker-controlled Python code in a model repo/path to execute at server startup.

---

# Impact

An attacker who can influence the model repo/path (local directory or remote Hugging Face repo) can achieve **arbitrary code execution** on the vLLM host during model load.  
This happens **before any request handling** and does **not require API access**.

---

# Affected Versions

All versions where `vllm/model_executor/models/registry.py` resolves `auto_map` entries with `try_get_class_from_dynamic_module` **without checking `trust_remote_code`** (at least current `main`).

---

# Details

During model resolution, vLLM unconditionally iterates `auto_map` entries from the model config and calls `try_get_class_from_dynamic_module`, which delegates to Transformers’ `get_class_from_dynamic_module` and **executes the module code**.

This occurs even when `trust_remote_code` is `false`, allowing a malicious model repo to embed code in a referenced module and have it executed during initialization.

### Relevant code

- `vllm/model_executor/models/registry.py:856` — auto_map resolution  
- `vllm/transformers_utils/dynamic_module.py:13` — delegates to `get_class_from_dynamic_module`, which executes code

---

# Fixes

* https://github.com/vllm-project/vllm/pull/32194

# Credits

Reported by **bugbunny.ai**

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-2pc9-4j83-qjmr
- https://nvd.nist.gov/vuln/detail/CVE-2026-22807
- https://github.com/vllm-project/vllm/pull/32194
- https://github.com/vllm-project/vllm/commit/78d13ea9de4b1ce5e4d8a5af9738fea71fb024e5
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-22807.json
- https://pypi.org/project/vllm
- https://github.com/vllm-project/vllm/releases/tag/v0.14.0
- https://github.com/vllm-project/vllm
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-2010.yaml
- https://github.com/advisories/GHSA-2pc9-4j83-qjmr
- https://bugzilla.redhat.com/show_bug.cgi?id=2431865
- https://access.redhat.com/security/cve/CVE-2026-22807
- https://access.redhat.com/errata/RHSA-2026:5119
- https://access.redhat.com/errata/RHSA-2026:42644
- https://access.redhat.com/errata/RHSA-2026:3782
- https://access.redhat.com/errata/RHSA-2026:3713
- https://access.redhat.com/errata/RHSA-2026:3462
- https://access.redhat.com/errata/RHSA-2026:3461
- https://access.redhat.com/errata/RHSA-2026:30089
- https://access.redhat.com/errata/RHSA-2026:30088
