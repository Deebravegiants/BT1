# [H] Gradio Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-f3h9-8phc-6gvh
CVE: CVE-2024-0964
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-06
Source: https://github.com/advisories/GHSA-f3h9-8phc-6gvh
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <4.9.0

## Details
A local file include could be remotely triggered in Gradio due to a vulnerable user-supplied JSON value in an API request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-0964
- https://github.com/gradio-app/gradio/commit/d76bcaaaf0734aaf49a680f94ea9d4d22a602e70
- https://github.com/gradio-app/gradio
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2024-261.yaml
- https://huntr.com/bounties/25e25501-5918-429c-8541-88832dfd3741
