# [M] OpenStack Barbican information disclosure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6rx9-c2rh-3qv4
CVE: CVE-2023-1636
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2023-09-24
Source: https://github.com/advisories/GHSA-6rx9-c2rh-3qv4
Type: github-advisory

## Affected
- PyPI: `barbican` — affected >=0

## Details
A vulnerability was found in OpenStack Barbican containers. This vulnerability is only applicable to deployments that utilize an all-in-one configuration. Barbican containers share the same CGROUP, USER, and NET namespace with the host system and other OpenStack services. If any service is compromised, it could gain access to the data transmitted to and from Barbican.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1636
- https://access.redhat.com/security/cve/CVE-2023-1636
- https://bugzilla.redhat.com/show_bug.cgi?id=2181765
- https://github.com/openstack/barbican
