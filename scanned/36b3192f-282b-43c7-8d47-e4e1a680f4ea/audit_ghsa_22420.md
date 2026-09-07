# [H] Arbitrary file overwrite in OpenStack Nova

## Summary
Severity: High
Advisory: GHSA-xc4g-7vw8-924h
CVE: CVE-2012-3447
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-xc4g-7vw8-924h
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <12.0.0

## Details
`virt/disk/api.py` in OpenStack Compute (Nova) 2012.1.x before 2012.1.2 and Folsom before Folsom-3 allows remote authenticated users to overwrite arbitrary files via a symlink attack on a file in an image that uses a symlink that is only readable by root.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2012-3361.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-3447
- https://github.com/openstack/nova/commit/ce4b2e27be45a85b310237615c47eb53f37bb5f3
- https://github.com/openstack/nova/commit/d9577ce9f266166a297488445b5b0c93c1ddb368
- https://bugs.launchpad.net/nova/+bug/1031311
- https://bugzilla.redhat.com/show_bug.cgi?id=845106
- https://exchange.xforce.ibmcloud.com/vulnerabilities/77539
- https://github.com/openstack/nova
- https://github.com/pypa/advisory-database/tree/main/vulns/nova/PYSEC-2012-21.yaml
- https://review.openstack.org/#/c/10953
- https://web.archive.org/web/20120824003029/http://www.securityfocus.com/bid/54869
- http://www.openwall.com/lists/oss-security/2012/08/07/1
