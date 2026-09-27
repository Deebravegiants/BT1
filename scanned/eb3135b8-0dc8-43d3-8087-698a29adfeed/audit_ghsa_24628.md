# [H] Eclipse Vorto resolved Maven build artifacts for the Xtext project over HTTP instead of HTTPS

## Summary
Severity: High
Advisory: GHSA-fg2q-v428-2gph
CVE: CVE-2019-10248
CWE: CWE-494, CWE-669, CWE-829
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fg2q-v428-2gph
Type: github-advisory

## Affected
- Maven: `org.eclipse.vorto:org.eclipse.vorto.core` — affected >=0 <0.11.0

## Details
Eclipse Vorto versions prior to 0.11 resolved Maven build artifacts for the Xtext project over HTTP instead of HTTPS. Any of these dependent artifacts could have been maliciously compromised by a MITM attack. Hence produced build artifacts of Vorto might be infected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10248
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=546622
- https://github.com/eclipse/vorto
