# [M] Pyload contains Sensitive Cookie in HTTPS Session Without 'Secure' Attribute

## Summary
Severity: Medium
Advisory: GHSA-m3g7-wrrq-v5c8
CVE: CVE-2023-0055
CWE: CWE-319, CWE-614
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-01-05
Source: https://github.com/advisories/GHSA-m3g7-wrrq-v5c8
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0 <0.5.0b3.dev32

## Details
Sensitive Cookie in HTTPS Session Without 'Secure' Attribute in GitHub repository pyload/pyload prior to 0.5.0b3.dev32. The Secure attribute for sensitive cookies in HTTPS sessions is not set, which could cause the user agent to send those cookies in plaintext over an HTTP session. This issue is patched in version 0.5.0b3.dev32.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0055
- https://github.com/pyload/pyload/commit/7b53b8d43c2c072b457dcd19c8a09bcfc3721703
- https://github.com/pyload/pyload
- https://huntr.dev/bounties/ed88e240-99ff-48a1-bf32-8e1ef5f13cce
