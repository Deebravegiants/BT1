# [H] OpenStack Nova Server Resource Faults Leak External Exception Details

## Summary
Severity: High
Advisory: GHSA-pg64-r7rr-phv8
CVE: CVE-2019-14433
CWE: CWE-200, CWE-209
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pg64-r7rr-phv8
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <17.0.12
- PyPI: `nova` — affected >=18.0.0 <18.2.2
- PyPI: `nova` — affected >=19.0.0 <19.0.2

## Details
An issue was discovered in OpenStack Nova before 17.0.12, 18.x before 18.2.2, and 19.x before 19.0.2. If an API request from an authenticated user ends in a fault condition due to an external exception, details of the underlying environment may be leaked in the response, and could include sensitive configuration or other data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14433
- https://github.com/openstack/nova/commit/298b337a16c0d10916b4431c436d19b3d6f5360e
- https://access.redhat.com/errata/RHSA-2019:2622
- https://access.redhat.com/errata/RHSA-2019:2631
- https://access.redhat.com/errata/RHSA-2019:2652
- https://github.com/openstack/nova
- https://github.com/pypa/advisory-database/tree/main/vulns/nova/PYSEC-2019-191.yaml
- https://launchpad.net/bugs/1837877
- https://lists.debian.org/debian-lts-announce/2022/09/msg00018.html
- https://security.openstack.org/ossa/OSSA-2019-003.html
- https://usn.ubuntu.com/4104-1
- http://www.openwall.com/lists/oss-security/2019/08/06/6
