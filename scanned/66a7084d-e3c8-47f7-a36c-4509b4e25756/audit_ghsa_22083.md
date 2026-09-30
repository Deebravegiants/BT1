# [M] OpenStack Glance Signature Verification Bypass

## Summary
Severity: Medium
Advisory: GHSA-wmhw-fvg9-87fc
CVE: CVE-2015-8234
CWE: CWE-328
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-wmhw-fvg9-87fc
Type: github-advisory

## Affected
- PyPI: `glance` — affected >=0

## Details
The image signature algorithm in OpenStack Glance 11.0.0 allows remote attackers to bypass the signature verification process via a crafted image, which triggers an MD5 collision.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8234
- https://bugs.launchpad.net/glance/+bug/1516031
- https://github.com/pypa/advisory-database/tree/main/vulns/glance/PYSEC-2017-143.yaml
- https://seclists.org/oss-sec/2015/q4/303
- https://wiki.openstack.org/wiki/OSSN/OSSN-0061
- http://seclists.org/oss-sec/2015/q4/303
