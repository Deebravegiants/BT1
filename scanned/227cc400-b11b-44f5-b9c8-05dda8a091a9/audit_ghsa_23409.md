# [M] OpenStack Horizon Cross-site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-47vp-44v9-rhgq
CVE: CVE-2017-7400
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-47vp-44v9-rhgq
Type: github-advisory

## Affected
- PyPI: `horizon` — affected >=9.0 <9.1.2
- PyPI: `horizon` — affected >=10.0 <10.0.3
- PyPI: `horizon` — affected >=11.0.0 <11.0.1

## Details
OpenStack Horizon 9.x through 9.1.1, 10.x through 10.0.2, and 11.0.0 allows remote authenticated administrators to conduct XSS attacks via a crafted federation mapping.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7400
- https://access.redhat.com/errata/RHSA-2017:1598
- https://access.redhat.com/errata/RHSA-2017:1739
- https://launchpad.net/bugs/1667086
- https://opendev.org/openstack/horizon/commit/1407cfe53144146b29679de21f28c952282043ae
- https://opendev.org/openstack/horizon/commit/511b325b45b6bd7a88bb6df1a4639b80d0121277
- https://opendev.org/openstack/horizon/commit/a835dbfbaa2c70329c08d4b8429d49315dc6d651
- https://opendev.org/openstack/horizon/commit/ce80bb6fec3cb0262728e7ae8b9d695cf832e5bf
- http://www.securityfocus.com/bid/97324
