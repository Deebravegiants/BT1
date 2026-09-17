# [M] OpenStack Identity (Keystone) Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-7332-36h8-8jh8
CVE: CVE-2013-2014
CWE: CWE-20
Ecosystem: PyPI
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-7332-36h8-8jh8
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=0 <8.0.0a0

## Details
OpenStack Identity (Keystone) before 2013.1 allows remote attackers to cause a denial of service (memory consumption and crash) via multiple long requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2014
- https://github.com/openstack/keystone/commit/7691276b869a86c2b75631d5bede9f61e030d9d8
- https://bugs.launchpad.net/keystone/+bug/1098177
- https://bugs.launchpad.net/keystone/+bug/1099025
- https://exchange.xforce.ibmcloud.com/vulnerabilities/84347
- http://lists.fedoraproject.org/pipermail/package-announce/2013-July/111914.html
- http://secunia.com/advisories/53397
- http://www.securityfocus.com/bid/59936
