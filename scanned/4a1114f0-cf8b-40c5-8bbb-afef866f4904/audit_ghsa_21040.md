# [H] Barbican authorization flaw before v14.0.0

## Summary
Severity: High
Advisory: GHSA-p2jg-q8hw-p7gc
CVE: CVE-2022-23451
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-09-07
Source: https://github.com/advisories/GHSA-p2jg-q8hw-p7gc
Type: github-advisory

## Affected
- PyPI: `barbican` — affected >=0 <14.0.0

## Details
An authorization flaw was found in openstack-barbican. The default policy rules for the secret metadata API allowed any authenticated user to add, modify, or delete metadata from any secret regardless of ownership. This flaw allows an attacker on the network to modify or delete protected data, causing a denial of service by consuming protected resources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23451
- https://github.com/openstack/barbican/commit/7d270bacbe29a90a10f1855abc3b50dac0f08022
- https://access.redhat.com/errata/RHSA-2022:5114
- https://access.redhat.com/errata/RHSA-2022:8874
- https://access.redhat.com/security/cve/CVE-2022-23451
- https://bugzilla.redhat.com/show_bug.cgi?id=2022878
- https://bugzilla.redhat.com/show_bug.cgi?id=2025089
- https://github.com/openstack/barbican
- https://review.opendev.org/c/openstack/barbican/+/811236
