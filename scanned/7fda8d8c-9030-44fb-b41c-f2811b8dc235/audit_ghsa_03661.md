# [M] Improper Certificate Validation and Insufficient Verification of Data Authenticity in Keycloak

## Summary
Severity: Medium
Advisory: GHSA-38cg-gg9j-q9j9
CVE: CVE-2019-3875
CWE: CWE-295, CWE-345
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2019-06-27
Source: https://github.com/advisories/GHSA-38cg-gg9j-q9j9
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0

## Details
A vulnerability was found in keycloak before 6.0.2. The X.509 authenticator supports the verification of client certificates through the CRL, where the CRL list can be obtained from the URL provided in the certificate itself (CDP) or through the separately configured path. The CRL are often available over the network through unsecured protocols ('http' or 'ldap') and hence the caller should verify the signature and possibly the certification path. Keycloak currently doesn't validate signatures on CRL, which can result in a possibility of various attacks like man-in-the-middle.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3875
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3875
