# [M] Jinja2 vulnerable to sandbox breakout through attr filter selecting format method

## Summary
Severity: Medium
Advisory: GHSA-cpwx-vrp4-4pq7
CVE: CVE-2025-27516
CWE: CWE-1336
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-03-05
Source: https://github.com/advisories/GHSA-cpwx-vrp4-4pq7
Type: github-advisory

## Affected
- PyPI: `Jinja2` — affected >=0 <3.1.6

## Details
An oversight in how the Jinja sandboxed environment interacts with the `|attr` filter allows an attacker that controls the content of a template to execute arbitrary Python code.

To exploit the vulnerability, an attacker needs to control the content of a template. Whether that is the case depends on the type of application using Jinja. This vulnerability impacts users of applications which execute untrusted templates.

Jinja's sandbox does catch calls to `str.format` and ensures they don't escape the sandbox. However, it's possible to use the `|attr` filter to get a reference to a string's plain format method, bypassing the sandbox. After the fix, the `|attr` filter no longer bypasses the environment's attribute lookup.

## References
- https://github.com/pallets/jinja/security/advisories/GHSA-cpwx-vrp4-4pq7
- https://nvd.nist.gov/vuln/detail/CVE-2025-27516
- https://github.com/pallets/jinja/commit/90457bbf33b8662926ae65cdde4c4c32e756e403
- https://github.com/pallets/jinja
- https://lists.debian.org/debian-lts-announce/2025/04/msg00022.html
- https://lists.debian.org/debian-lts-announce/2025/04/msg00045.html
