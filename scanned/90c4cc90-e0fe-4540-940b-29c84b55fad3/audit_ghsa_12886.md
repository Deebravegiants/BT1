# [M] Path Traversal In Eclipse GlassFish

## Summary
Severity: Medium
Advisory: GHSA-3g5w-6pw7-6hrp
CVE: CVE-2022-2712
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-27
Source: https://github.com/advisories/GHSA-3g5w-6pw7-6hrp
Type: github-advisory

## Affected
- Maven: `org.glassfish.main.web:web` — affected >=5.1.0 <7.0.0

## Details
In Eclipse GlassFish versions 5.1.0 to 6.2.5, there is a vulnerability in relative path traversal because it does not filter request path starting with './'. Successful exploitation could allow an remote unauthenticated attacker to access critical data, such as configuration files and deployed application source code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2712
- https://github.com/eclipse-ee4j/glassfish/pull/24077
- https://bugs.eclipse.org/580502
