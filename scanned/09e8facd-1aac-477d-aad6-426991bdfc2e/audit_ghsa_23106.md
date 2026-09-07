# [H] OpenStack Keystone Insufficient token expiration

## Summary
Severity: High
Advisory: GHSA-w66p-78g4-mr7g
CVE: CVE-2012-5563
CWE: CWE-324, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-w66p-78g4-mr7g
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=0 <8.0.0

## Details
OpenStack Keystone, as used in OpenStack Folsom 2012.2, does not properly implement token expiration, which allows remote authenticated users to bypass intended authorization restrictions by creating new tokens through token chaining.  NOTE: this issue exists because of a CVE-2012-3426 regression.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5563
- https://github.com/openstack/keystone/commit/38c7e46a640a94da4da89a39a5a1ea9c081f1eb5
- https://github.com/openstack/keystone/commit/f9d4766249a72d8f88d75dcf1575b28dd3496681
- https://bugs.launchpad.net/keystone/+bug/1079216
- https://exchange.xforce.ibmcloud.com/vulnerabilities/80370
- https://github.com/openstack/keystone
- https://github.com/pypa/advisory-database/tree/main/vulns/keystone/PYSEC-2012-20.yaml
- https://web.archive.org/web/20121201003009/http://secunia.com/advisories/51423
- https://web.archive.org/web/20140802122732/http://secunia.com/advisories/51436
- https://web.archive.org/web/20200228144943/http://www.securityfocus.com/bid/56727
- http://rhn.redhat.com/errata/RHSA-2012-1557.html
- http://www.openwall.com/lists/oss-security/2012/11/28/5
- http://www.openwall.com/lists/oss-security/2012/11/28/6
- http://www.ubuntu.com/usn/USN-1641-1
