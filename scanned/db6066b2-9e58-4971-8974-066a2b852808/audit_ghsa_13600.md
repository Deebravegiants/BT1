# [M] light-oauth2 missing public key verification

## Summary
Severity: Medium
Advisory: GHSA-mx47-h5fv-ghwh
CVE: CVE-2023-31580
CWE: CWE-295, CWE-347
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-25
Source: https://github.com/advisories/GHSA-mx47-h5fv-ghwh
Type: github-advisory

## Affected
- Maven: `com.networknt:light-oauth2` — affected >=0 <2.1.27

## Details
light-oauth2 before version 2.1.27 obtains the public key without any verification. This could allow attackers to authenticate to the application with a crafted JWT token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31580
- https://github.com/networknt/light-oauth2/issues/369
- https://github.com/KANIXB/JWTIssues/blob/main/Certification%20Verification%20issue%20in%20light-oauth2.md
- https://github.com/networknt/light-oauth2
