# [M] LdapCherry Cross-site Scripting vulnerbaility

## Summary
Severity: Medium
Advisory: GHSA-vq8w-x8v7-f88m
CVE: CVE-2019-25095
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-01-05
Source: https://github.com/advisories/GHSA-vq8w-x8v7-f88m
Type: github-advisory

## Affected
- PyPI: `ldapcherry` — affected >=0 <1.0.0

## Details
A vulnerability, which was classified as problematic, was found in kakwa LdapCherry up to 0.x. Affected is an unknown function of the component URL Handler. The manipulation leads to cross site scripting. It is possible to launch the attack remotely. Upgrading to version 1.0.0 is able to address this issue. The name of the patch is 6f98076281e9452fdb1adcd1bcbb70a6f968ade9. It is recommended to upgrade the affected component. VDB-217434 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25095
- https://github.com/kakwa/ldapcherry/pull/16
- https://github.com/kakwa/ldapcherry/commit/6f98076281e9452fdb1adcd1bcbb70a6f968ade9
- https://github.com/kakwa/ldapcherry
- https://github.com/kakwa/ldapcherry/releases/tag/1.0.0
- https://github.com/pypa/advisory-database/tree/main/vulns/ldapcherry/PYSEC-2023-19.yaml
- https://vuldb.com/?ctiid.217434
- https://vuldb.com/?id.217434
