# [M] Jenkins mabl Plugin vulnerable to exposure of system-scooped credentials

## Summary
Severity: Medium
Advisory: GHSA-4c3q-r84r-q6pp
CVE: CVE-2023-37951
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-4c3q-r84r-q6pp
Type: github-advisory

## Affected
- Maven: `com.mabl.integration.jenkins:mabl-integration` — affected >=0 <0.0.47

## Details
Jenkins mabl Plugin 0.0.46 and earlier does not set the appropriate context for credentials lookup, allowing the use of System-scoped credentials otherwise reserved for the global configuration.

This allows attackers with Item/Configure permission to access and capture credentials they are not entitled to.

mabl Plugin 0.0.47 defines the appropriate context for credentials lookup.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37951
- https://www.jenkins.io/security/advisory/2023-07-12/#SECURITY-3137%20(2)
- http://www.openwall.com/lists/oss-security/2023/07/12/2
