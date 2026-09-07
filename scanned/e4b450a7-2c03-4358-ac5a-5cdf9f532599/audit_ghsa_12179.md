# [H] ONNX Untrusted Model Repository Warnings Suppressed by silent=True in onnx.hub.load() — Silent Supply-Chain Attack

## Summary
Severity: High
Advisory: GHSA-hqmj-h5c6-369m
CVE: CVE-2026-28500
CWE: CWE-345, CWE-494, CWE-693
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-hqmj-h5c6-369m
Type: github-advisory

## Affected
- PyPI: `onnx` — affected >=0 <1.21.0rc1

## Details
## What's the issue
Passing `silent=True` to `onnx.hub.load()` kills all trust warnings and user prompts. This means a model can be downloaded from any unverified GitHub repo with zero user awareness.
 
```python
if not _verify_repo_ref(repo) and not silent:
    # completely skipped when silent=True
    print("The model repo... is not trusted")
    if input().lower() != "y":
        return None
```
 
On top of that, the SHA256 integrity check is useless here — it validates against a manifest that lives in the same repo the attacker controls, so the hash will always match.

 
## Impact
Any pipeline using `hub.load()` with `silent=True` and an external repo string is silently loading whatever the repo owner ships. If that model executes arbitrary code on load, the attacker has access to the machine.
 
## Resolved by removing the feature 
## References
 
- [Write-up](https://github.com/ZeroXJacks/CVEs/blob/main/2026/CVE-2026-28500.md)

## References
- https://github.com/onnx/onnx/security/advisories/GHSA-hqmj-h5c6-369m
- https://nvd.nist.gov/vuln/detail/CVE-2026-28500
- https://github.com/ZeroXJacks/CVEs/blob/main/2026/CVE-2026-28500.md
- https://github.com/onnx/onnx
- https://github.com/pypa/advisory-database/tree/main/vulns/onnx/PYSEC-2026-103.yaml
