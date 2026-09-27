# [M] OpenStack Glance v2 API unrestricted path traversal through filesystem:// scheme

## Summary
Severity: Medium
Advisory: GHSA-pwrj-f53c-f89j
CVE: CVE-2015-1195
CWE: CWE-22
Ecosystem: PyPI
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-pwrj-f53c-f89j
Type: github-advisory

## Affected
- PyPI: `glance` — affected >=0 <11.0.0a0

## Details
The V2 API in OpenStack Image Registry and Delivery Service (Glance) before 2014.1.4 and 2014.2.x before 2014.2.2 allows remote authenticated users to read or delete arbitrary files via a full pathname in a `filesystem://` URL in the image location property.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2014-9493.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1195
- https://github.com/openstack/glance/commit/5191ed1879c5fd5b2694f922bcedec232f461088
- https://github.com/openstack/glance/commit/7d3a1db33ccbd25b9fc7326ce3468eabd2a41a99
- https://github.com/openstack/glance/commit/a2d986b976e9325a272e2d422465165315d19fe6
- https://bugs.launchpad.net/ossa/+bug/1408663
- https://github.com/openstack/glance
- http://lists.openstack.org/pipermail/openstack-announce/2015-January/000325.html
- http://secunia.com/advisories/62169
- http://www.openwall.com/lists/oss-security/2015/01/15/2
- http://www.openwall.com/lists/oss-security/2015/01/18/5
- http://www.oracle.com/technetwork/topics/security/bulletinapr2015-2511959.html
- http://www.securityfocus.com/bid/71976
