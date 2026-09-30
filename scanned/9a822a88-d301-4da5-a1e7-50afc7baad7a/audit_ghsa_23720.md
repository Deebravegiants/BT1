# [H] SimpleGeo python-oauth2 does not check the nonce allowing replay attacks

## Summary
Severity: High
Advisory: GHSA-4433-4cxq-vv73
CVE: CVE-2013-4346
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4433-4cxq-vv73
Type: github-advisory

## Affected
- PyPI: `oauth2` — affected >=0

## Details
The Server.verify_request function in SimpleGeo python-oauth2 does not check the nonce, which allows remote attackers to perform replay attacks via a signed URL.
The vulnerability does not appear to be patched according to the following [discussion](https://github.com/joestump/python-oauth2/issues/129#issuecomment-895911502).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4346
- https://github.com/simplegeo/python-oauth2/issues/129
- https://access.redhat.com/errata/RHSA-2015:1591
- https://access.redhat.com/errata/RHSA-2015:1592
- https://access.redhat.com/security/cve/CVE-2013-4346
- https://bugzilla.redhat.com/show_bug.cgi?id=1007746
- https://github.com/joestump/python-oauth2
- https://github.com/pypa/advisory-database/tree/main/vulns/oauth2/PYSEC-2014-85.yaml
- https://web.archive.org/web/20200228063302/http://www.securityfocus.com/bid/62386
- http://www.openwall.com/lists/oss-security/2013/09/12/7
