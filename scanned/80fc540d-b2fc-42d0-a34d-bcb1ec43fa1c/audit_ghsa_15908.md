# [H] DOMpurify has a nesting-based mXSS

## Summary
Severity: High
Advisory: GHSA-gx9m-whjm-85jf
CVE: CVE-2024-47875
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:H (CVSS_V3)
Published: 2024-10-11
Source: https://github.com/advisories/GHSA-gx9m-whjm-85jf
Type: github-advisory

## Affected
- npm: `dompurify` — affected >=0 <2.5.0
- npm: `dompurify` — affected >=3.0.0 <3.1.3

## Details
DOMpurify was vulnerable to nesting-based mXSS 

fixed by [0ef5e537](https://github.com/cure53/DOMPurify/tree/0ef5e537a514f904b6aa1d7ad9e749e365d7185f) (2.x) and
[merge 943](https://github.com/cure53/DOMPurify/pull/943)

Backporter should be aware of GHSA-mmhx-hmjr-r674 (CVE-2024-45801) when cherry-picking

POC is avaible under [test](https://github.com/cure53/DOMPurify/blob/0ef5e537a514f904b6aa1d7ad9e749e365d7185f/test/test-suite.js#L2098)

## References
- https://github.com/cure53/DOMPurify/security/advisories/GHSA-gx9m-whjm-85jf
- https://nvd.nist.gov/vuln/detail/CVE-2024-47875
- https://github.com/cure53/DOMPurify/commit/0ef5e537a514f904b6aa1d7ad9e749e365d7185f
- https://github.com/cure53/DOMPurify/commit/6ea80cd8b47640c20f2f230c7920b1f4ce4fdf7a
- https://github.com/cure53/DOMPurify
- https://github.com/cure53/DOMPurify/blob/0ef5e537a514f904b6aa1d7ad9e749e365d7185f/test/test-suite.js#L2098
- https://lists.debian.org/debian-lts-announce/2025/02/msg00010.html
- http://seclists.org/fulldisclosure/2025/Apr/14
