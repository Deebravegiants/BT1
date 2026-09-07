# [M] OpenStack Compute (Nova) does not verify the virtual size of a QCOW2 image

## Summary
Severity: Medium
Advisory: GHSA-m674-hmx2-ffhq
CVE: CVE-2013-2096
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-m674-hmx2-ffhq
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <12.0.0a0

## Details
OpenStack Compute (Nova) Folsom, Grizzly, and Havana does not verify the virtual size of a QCOW2 image, which allows local users to cause a denial of service (host file system disk consumption) by creating an image with a large virtual size that does not contain a large amount of data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2096
- https://github.com/openstack/nova/commit/0caeb8eaf20abcdc77828f5c6b79fc104619e231
- https://github.com/openstack/nova/commit/44a8aba1d5da87d54db48079103fdef946666d80
- https://github.com/openstack/nova
- https://review.openstack.org/#/c/28717
- https://review.openstack.org/#/c/28901
- https://review.openstack.org/#/c/29192
- https://web.archive.org/web/20130726040108/http://www.securityfocus.com/bid/59924
- http://lists.openstack.org/pipermail/openstack-announce/2013-May/000102.html
- http://www.ubuntu.com/usn/USN-1831-1
