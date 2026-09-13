# [M] OpenStack Neutron has an Incorrect Authorization issue

## Summary
Severity: Medium
Advisory: GHSA-xv24-hxh9-2hh9
CVE: CVE-2026-49299
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-xv24-hxh9-2hh9
Type: github-advisory

## Affected
- PyPI: `neutron` — affected >=28.0.0 <28.0.1
- PyPI: `neutron` — affected >=27.0.0 <27.0.3
- PyPI: `neutron` — affected >=26.0.0 <26.0.4

## Details
In OpenStack Neutron before 28.0.1, the tagging controller enforces plural policy action names on single-tag write operations while the defined policy rules use singular names. The mismatched names evaluate as allowed under the default policy, permitting a project reader to create and update tags on same-project resources. Deployments running Neutron 26.0.0 or later are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-49299
- https://bugs.launchpad.net/bugs/2150132
- https://github.com/openstack/neutron
- https://review.opendev.org/c/openstack/neutron/+/989099
- https://www.openwall.com/lists/oss-security/2026/05/28/8
- http://www.openwall.com/lists/oss-security/2026/06/02/7
