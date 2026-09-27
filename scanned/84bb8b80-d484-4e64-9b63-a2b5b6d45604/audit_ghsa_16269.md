# [M] jose4j denial of service via specifically crafted JWE

## Summary
Severity: Medium
Advisory: GHSA-6qvw-249j-h44c
CVE: CVE-2023-51775
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-29
Source: https://github.com/advisories/GHSA-6qvw-249j-h44c
Type: github-advisory

## Affected
- Maven: `org.bitbucket.b_c:jose4j` — affected >=0 <0.9.4

## Details
The jose4j component before 0.9.4 for Java allows attackers to cause a denial of service (CPU consumption) via a large p2c (aka PBES2 Count) value.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-51775
- https://bitbucket.org/b_c/jose4j/commits/1afaa1e174b3
- https://bitbucket.org/b_c/jose4j/issues/212
- https://security.netapp.com/advisory/ntap-20241108-0002
