# [M] OpenStack Glance arbitrary deletion of non-protected images

## Summary
Severity: Medium
Advisory: GHSA-6rrm-xxvh-7r87
CVE: CVE-2012-4573
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6rrm-xxvh-7r87
Type: github-advisory

## Affected
- PyPI: `glance` — affected >=0 <11.0.0a0

## Details
The v1 API in OpenStack Glance Grizzly, Folsom (2012.2), and Essex (2012.1) allows remote authenticated users to delete arbitrary non-protected images via an image deletion request, a different vulnerability than CVE-2012-5482.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-4573
- https://github.com/openstack/glance/commit/6ab0992e5472ae3f9bef0d2ced41030655d9d2bc
- https://github.com/openstack/glance/commit/90bcdc5a89e350a358cf320a03f5afe99795f6f6
- https://github.com/openstack/glance/commit/efd7e75b1f419a52c7103c7840e24af8e5deb29d
- https://bugs.launchpad.net/glance/+bug/1065187
- https://exchange.xforce.ibmcloud.com/vulnerabilities/79895
- https://github.com/openstack/glance
- https://github.com/pypa/advisory-database/tree/main/vulns/glance/PYSEC-2012-29.yaml
- http://lists.fedoraproject.org/pipermail/package-announce/2012-November/092192.html
- http://lists.opensuse.org/opensuse-security-announce/2012-11/msg00002.html
- http://osvdb.org/87248
- http://packetstormsecurity.com/files/118733/Red-Hat-Security-Advisory-2012-1558-01.html
- http://rhn.redhat.com/errata/RHSA-2012-1558.html
- http://secunia.com/advisories/51174
- http://secunia.com/advisories/51234
- http://www.openwall.com/lists/oss-security/2012/11/07/6
- http://www.openwall.com/lists/oss-security/2012/11/09/5
- http://www.securityfocus.com/bid/56437
- http://www.ubuntu.com/usn/USN-1626-1
- http://www.ubuntu.com/usn/USN-1626-2
