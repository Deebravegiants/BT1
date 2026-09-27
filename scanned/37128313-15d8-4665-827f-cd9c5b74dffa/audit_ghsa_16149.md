# [M] libre-chat Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3864-rp2m-2qfj
CVE: CVE-2024-52787
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-11-25
Source: https://github.com/advisories/GHSA-3864-rp2m-2qfj
Type: github-advisory

## Affected
- PyPI: `libre-chat` — affected >=0

## Details
An issue in the upload_documents method of libre-chat v0.0.6 allows attackers to execute a path traversal via supplying a crafted filename in an uploaded file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-52787
- https://github.com/vemonet/libre-chat/issues/10
- https://github.com/vemonet/libre-chat/pull/9
- https://github.com/vemonet/libre-chat/commit/dbb8e3400e5258112179783d74c9cc54310cb72b
- https://gist.github.com/jxfzzzt/276a6e8cfbc54d2c2711bb51d8d3dff3
- https://github.com/vemonet/libre-chat
