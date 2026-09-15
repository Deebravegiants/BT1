# [M] OpenStack Nova vulnerable to unauthorized access to potentially sensitive data 

## Summary
Severity: Medium
Advisory: GHSA-rm86-h44c-2r2m
CVE: CVE-2024-40767
CWE: CWE-436, CWE-552
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-24
Source: https://github.com/advisories/GHSA-rm86-h44c-2r2m
Type: github-advisory

## Affected
- PyPI: `Nova` — affected >=0
- PyPI: `Nova` — affected >=28.0.0
- PyPI: `Nova` — affected >=29.0.0

## Details
In OpenStack Nova before 27.4.1, 28 before 28.2.1, and 29 before 29.1.1, by supplying a raw format image that is actually a crafted QCOW2 image with a backing file path or VMDK flat image with a descriptor file path, an authenticated user may convince systems to return a copy of the referenced file's contents from the server, resulting in unauthorized access to potentially sensitive data. All Nova deployments are affected. NOTE: this issue exists because of an incomplete fix for CVE-2022-47951 and CVE-2024-32498.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-40767
- https://github.com/openstack/nova
- https://launchpad.net/bugs/2071734
- https://lists.debian.org/debian-lts-announce/2024/09/msg00017.html
- https://review.opendev.org/c/openstack/nova/+/924731
- https://security.openstack.org
- https://security.openstack.org/ossa/OSSA-2024-002.html
- https://www.openwall.com/lists/oss-security/2024/07/23/2
