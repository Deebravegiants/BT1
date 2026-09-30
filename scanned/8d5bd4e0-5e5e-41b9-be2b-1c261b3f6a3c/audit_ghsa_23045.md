# [C] OpenStack Nova logs sensitive context from notification exceptions

## Summary
Severity: Critical
Advisory: GHSA-f4g4-cj8f-3cr9
CVE: CVE-2017-7214
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-f4g4-cj8f-3cr9
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=13.0.0 <13.1.4
- PyPI: `nova` — affected >=14.0.0 <14.0.5
- PyPI: `nova` — affected >=15.0.1 <15.0.2

## Details
An issue was discovered in exception_wrapper.py in OpenStack Nova 13.x through 13.1.3, 14.x through 14.0.4, and 15.x through 15.0.1. Legacy notification exception contexts appearing in ERROR level logs may include sensitive information such as account passwords and authorization tokens.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7214
- https://github.com/openstack/nova/commit/3f985f1eda6f29180878a3d21c20c5057179486a
- https://github.com/openstack/nova/commit/acb19160d4d348e29a21ad57c61c7369352c4d1c
- https://github.com/openstack/nova/commit/c2c91ce44592fc5dc2aacee1cf7f5b5cfd2e9a0a
- https://github.com/openstack/nova/commit/e193201fa1de5b08b29adefd8c149935c5529598
- https://access.redhat.com/errata/RHSA-2017:1508
- https://access.redhat.com/errata/RHSA-2017:1595
- https://github.com/openstack/nova
- https://launchpad.net/bugs/1673569
- http://www.securityfocus.com/bid/96998
