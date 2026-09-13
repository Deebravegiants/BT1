# [M] ONNX: Arbitrary File Read via ExternalData Hardlink Bypass in ONNX load

## Summary
Severity: Medium
Advisory: GHSA-cmw6-hcpp-c6jp
CVE: CVE-2026-34446
CWE: CWE-22, CWE-61
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-cmw6-hcpp-c6jp
Type: github-advisory

## Affected
- PyPI: `onnx` — affected >=0 <1.21.0

## Details
### Summary
The issue is in `onnx.load` — the code checks for symlinks to prevent path traversal, but completely misses hardlinks, which is the problem, since a hardlink looks exactly like a regular file on the filesystem.

### The Real Problem
The validator in `onnx/checker.cc` only calls `is_symlink()` and never checks the inode or `st_nlink`, so a hardlink walks right through every security check without any issues.

### Impact
Especially dangerous in AI supply chain scenarios like HuggingFace — a single malicious model is enough to silently steal secrets from the victim's machine without them noticing anything.

## References
- https://github.com/onnx/onnx/security/advisories/GHSA-cmw6-hcpp-c6jp
- https://nvd.nist.gov/vuln/detail/CVE-2026-34446
- https://github.com/onnx/onnx/commit/4755f8053928dce18a61db8fec71b69c74f786cb
- https://github.com/onnx/onnx
