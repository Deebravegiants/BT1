# [M] OpenStack Glance is affected by Server-Side Request Forgery (SSRF)

## Summary
Severity: Medium
Advisory: GHSA-mc26-q38v-83gv
CVE: CVE-2026-34881
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-mc26-q38v-83gv
Type: github-advisory

## Affected
- PyPI: `glance` — affected >=0 <29.2.0
- PyPI: `glance` — affected >=30.0.0 <30.2.0
- PyPI: `glance` — affected >=31.0.0 <31.1.0

## Details
OpenStack Glance versions < 29.1.1, >= 30.0.0 < 30.1.1, == 31.0.0 are affected by Server-Side Request Forgery (SSRF). By use of HTTP redirects, an authenticated user can bypass URL validation checks and redirect to internal services. Only the glance image import functionality is affected. In particular, the web-download and glance-download import methods are subject to this vulnerability, as is the optional (not enabled by default) ovf_process image import plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-34881
- https://bugs.launchpad.net/glance/+bug/2138602
- https://github.com/openstack/glance
- https://security.openstack.org/ossa/OSSA-2026-004.html
