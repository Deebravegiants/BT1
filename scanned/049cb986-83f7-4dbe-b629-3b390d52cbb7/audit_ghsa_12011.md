# [H] vLLM has Hardcoded Trust Override in Model Files Enables RCE Despite Explicit User Opt-Out

## Summary
Severity: High
Advisory: GHSA-7972-pg2x-xr59
CVE: CVE-2026-27893
CWE: CWE-693
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-7972-pg2x-xr59
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.10.1 <0.18.0

## Details
### Summary

  Two model implementation files hardcode `trust_remote_code=True` when loading sub-components, bypassing the user's explicit `--trust-remote-code=False` security opt-out. This enables remote code execution via malicious model
  repositories even when the user has explicitly disabled remote code trust.

  ### Details

  **Affected files (latest main branch):**

  1. `vllm/model_executor/models/nemotron_vl.py:430`
  ```python
  vision_model = AutoModel.from_config(config.vision_config, trust_remote_code=True)
```

  2. vllm/model_executor/models/kimi_k25.py:177
 
```python
  cached_get_image_processor(self.ctx.model_config.model, trust_remote_code=True)
```

  Both pass a hardcoded trust_remote_code=True to HuggingFace API calls, overriding the user's global --trust-remote-code=False setting.

  Relation to prior CVEs:
  - CVE-2025-66448 fixed auto_map resolution in vllm/transformers_utils/config.py (config loading path)
  - CVE-2026-22807 fixed broader auto_map at startup
  - Both fixes are present in the current code. These hardcoded instances in model files survived both patches — different code paths.

### Impact

  Remote code execution. An attacker can craft a malicious model repository that executes arbitrary Python code when loaded by vLLM, even when the user has explicitly set --trust-remote-code=False. This undermines the security guarantee
  that trust_remote_code=False is intended to provide.

  Remediation: Replace hardcoded trust_remote_code=True with self.config.model_config.trust_remote_code in both files. Raise a clear error if the model component requires remote code but the user hasn't opted in.

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-7972-pg2x-xr59
- https://nvd.nist.gov/vuln/detail/CVE-2026-27893
- https://github.com/vllm-project/vllm/pull/36192
- https://github.com/vllm-project/vllm/commit/00bd08edeee5dd4d4c13277c0114a464011acf72
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-27893.json
- https://github.com/vllm-project/vllm
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-2297.yaml
- https://bugzilla.redhat.com/show_bug.cgi?id=2452055
- https://access.redhat.com/security/cve/CVE-2026-27893
- https://access.redhat.com/errata/RHSA-2026:8748
- https://access.redhat.com/errata/RHSA-2026:8747
- https://access.redhat.com/errata/RHSA-2026:8746
- https://access.redhat.com/errata/RHSA-2026:37275
- https://access.redhat.com/errata/RHSA-2026:24977
- https://access.redhat.com/errata/RHSA-2026:19725
- https://access.redhat.com/errata/RHSA-2026:19724
- https://access.redhat.com/errata/RHSA-2026:19712
- https://access.redhat.com/errata/RHSA-2026:10141
- https://access.redhat.com/errata/RHSA-2026:10140
