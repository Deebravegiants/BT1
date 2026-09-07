# [H] Open WebUI Cross-Site Request Forgery (CSRF) Vulnerability

## Summary
Severity: High
Advisory: GHSA-85jc-8h5p-8vw8
CVE: CVE-2024-7806
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-85jc-8h5p-8vw8
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.3.33

## Details
A vulnerability in open-webui/open-webui versions <= 0.3.8 allows remote code execution by non-admin users via Cross-Site Request Forgery (CSRF). The application uses cookies with the SameSite attribute set to lax for authentication and lacks CSRF tokens. This allows an attacker to craft a malicious HTML that, when accessed by a victim, can modify the Python code of an existing pipeline and execute arbitrary code with the victim's privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7806
- https://github.com/open-webui/open-webui/pull/6054
- https://github.com/open-webui/open-webui/commit/7e253df17593bc12dc5cc89d28703675f05b0158
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/blob/1d20c27553f019477f01d7233ebe40b11d31e479/backend/main.py#L892-L920
- https://huntr.com/bounties/9350a68d-5f33-4b3d-988b-81e778160ab8
