# [H] Gunicorn HTTP Request/Response Smuggling vulnerability

## Summary
Severity: High
Advisory: GHSA-hc5x-x2vx-497g
CVE: CVE-2024-6827
CWE: CWE-444
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-hc5x-x2vx-497g
Type: github-advisory

## Affected
- PyPI: `gunicorn` — affected >=0 <22.0.0

## Details
Gunicorn version 21.2.0 does not properly validate the value of the 'Transfer-Encoding' header as specified in the RFC standards, which leads to the default fallback method of 'Content-Length,' making it vulnerable to TE.CL request smuggling. This vulnerability can lead to cache poisoning, data exposure, session manipulation, SSRF, XSS, DoS, data integrity compromise, security bypass, information leakage, and business logic abuse.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6827
- https://github.com/benoitc/gunicorn/issues/3087
- https://github.com/benoitc/gunicorn/issues/3278
- https://github.com/benoitc/gunicorn/pull/3113
- https://github.com/benoitc/gunicorn
- https://github.com/benoitc/gunicorn/releases/tag/22.0.0
- https://huntr.com/bounties/1b4f8f38-39da-44b6-9f98-f618639d0dd7
