# [M] OpenStack Barbican credential leak flaw

## Summary
Severity: Medium
Advisory: GHSA-6qqp-4vm3-359v
CVE: CVE-2023-1633
CWE: CWE-522
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2023-09-24
Source: https://github.com/advisories/GHSA-6qqp-4vm3-359v
Type: github-advisory

## Affected
- PyPI: `barbican` — affected >=0

## Details
A credentials leak flaw was found in OpenStack Barbican. This flaw allows a local authenticated attacker to read the configuration file, gaining access to sensitive credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1633
- https://access.redhat.com/security/cve/CVE-2023-1633
- https://bugzilla.redhat.com/show_bug.cgi?id=2181761
- https://github.com/openstack/barbican
