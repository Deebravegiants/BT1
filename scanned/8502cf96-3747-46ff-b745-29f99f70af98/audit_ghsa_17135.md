# [M] Information leakage in YAQL

## Summary
Severity: Medium
Advisory: GHSA-mvf6-hwxh-7v76
CVE: CVE-2024-29156
CWE: CWE-116, CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-03-18
Source: https://github.com/advisories/GHSA-mvf6-hwxh-7v76
Type: github-advisory

## Affected
- PyPI: `yaql` — affected >=0 <3.0.0

## Details
YAQL before 3.0.0 is used in Murano, the Murano service's MuranoPL extension to the YAQL language fails to sanitize the supplied environment, leading to potential leakage of sensitive service account information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29156
- https://bugs.launchpad.net/murano/+bug/2048114
- https://launchpad.net/bugs/2048114
- https://opendev.org/openstack/murano/tags
- https://opendev.org/openstack/yaql/commit/83e28324e1a0ce3970dd854393d2431123a909d3
- https://wiki.openstack.org/wiki/OSSN/OSSN-0093
