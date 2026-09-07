# [M] Ipsilon denial of service via a duplicate SP name

## Summary
Severity: Medium
Advisory: GHSA-6875-ff47-r6p6
CVE: CVE-2015-5217
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6875-ff47-r6p6
Type: github-advisory

## Affected
- PyPI: `ipsilon` — affected >=0.1.0 <1.2.0

## Details
providers/saml2/admin.py in the Identity Provider (IdP) server in Ipsilon 0.1.0 before 1.0.1 does not properly check permissions to update the SAML2 Service Provider (SP) owner, which allows remote authenticated users to cause a denial of service via a duplicate SP name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5217
- https://bugzilla.redhat.com/show_bug.cgi?id=1255172
- https://fedorahosted.org/ipsilon/wiki/Releases/v1.0.1
- https://github.com/ipsilon-project/ipsilon
- https://github.com/pypa/advisory-database/tree/main/vulns/ipsilon/PYSEC-2015-41.yaml
- https://pagure.io/ipsilon/826e6339441546f596320f3d73304ab5f7c10de6
- http://www.openwall.com/lists/oss-security/2015/10/27/8
