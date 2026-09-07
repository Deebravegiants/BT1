# [M] Ipsilon denial of service by deleting a SAML2 Service Provider (SP)

## Summary
Severity: Medium
Advisory: GHSA-9qp4-79q8-58pr
CVE: CVE-2015-5301
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9qp4-79q8-58pr
Type: github-advisory

## Affected
- PyPI: `ipsilon` — affected >=0.1.0 <1.0.2
- PyPI: `ipsilon` — affected >=1.1.0 <1.2.0

## Details
providers/saml2/admin.py in the Identity Provider (IdP) server in Ipsilon 0.1.0 before 1.0.2 and 1.1.x before 1.1.1 does not properly check permissions, which allows remote authenticated users to cause a denial of service by deleting a SAML2 Service Provider (SP).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5301
- https://bugzilla.redhat.com/show_bug.cgi?id=1271530
- https://fedorahosted.org/ipsilon/wiki/Releases/v1.0.2
- https://fedorahosted.org/ipsilon/wiki/Releases/v1.1.1
- https://github.com/ipsilon-project/ipsilon
- https://github.com/pypa/advisory-database/tree/main/vulns/ipsilon/PYSEC-2015-42.yaml
- https://pagure.io/ipsilon/9dec97c3c83928d231ea10f4160523a13803e594
- http://www.openwall.com/lists/oss-security/2015/10/27/8
