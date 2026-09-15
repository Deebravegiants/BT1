# [H] Sentencepiece has a a heap overflow issue

## Summary
Severity: High
Advisory: GHSA-38vq-g6vr-w8wf
CVE: CVE-2026-1260
CWE: CWE-119
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-22
Source: https://github.com/advisories/GHSA-38vq-g6vr-w8wf
Type: github-advisory

## Affected
- PyPI: `sentencepiece` — affected >=0 <0.2.1

## Details
Invalid memory access in Sentencepiece versions less than 0.2.1 when using a vulnerable model file, which is not created in the normal training procedure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1260
- https://github.com/google/sentencepiece/commit/d856b67fdb3492e035489abf9b3aaf486144b2c0
- https://github.com/google/sentencepiece
- https://github.com/google/sentencepiece/releases/tag/v0.2.1
