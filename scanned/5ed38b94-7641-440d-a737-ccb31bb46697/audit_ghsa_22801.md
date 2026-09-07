# [H] OpenStack Glance Denial of service by creating a large number of images

## Summary
Severity: High
Advisory: GHSA-h737-q6g6-8wr6
CVE: CVE-2014-9684
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-h737-q6g6-8wr6
Type: github-advisory

## Affected
- PyPI: `glance` — affected >=0 <11.0.0a0

## Details
OpenStack Image Registry and Delivery Service (Glance) 2014.2 through 2014.2.2 does not properly remove images, which allows remote authenticated users to cause a denial of service (disk consumption) by creating a large number of images using the task v2 API and then deleting them before the uploads finish, a different vulnerability than CVE-2015-1881.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9684
- https://github.com/openstack/glance/commit/7858d4d95154c8596720365e465cca7858cfec5c
- https://github.com/openstack/glance/commit/a880c8e762e94b70c1e5d5692a3defcde734a601
- https://bugs.launchpad.net/glance/+bug/1371118
- https://github.com/openstack/glance
- https://github.com/pypa/advisory-database/tree/main/vulns/glance/PYSEC-2015-37.yaml
- http://lists.openstack.org/pipermail/openstack-announce/2015-February/000336.html
- http://rhn.redhat.com/errata/RHSA-2015-0938.html
