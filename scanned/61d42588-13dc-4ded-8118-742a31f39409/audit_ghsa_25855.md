# [H] Temporary Directory Hijacking Vulnerability in Keycloak

## Summary
Severity: High
Advisory: GHSA-6xp6-fmc8-pmmr
CVE: CVE-2021-20202
CWE: CWE-377
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-6xp6-fmc8-pmmr
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <13.0.0

## Details
A flaw was found in keycloak. Directories can be created prior to the Java process creating them in the temporary directory, but with wider user permissions, allowing the attacker to have access to the contents that keycloak stores in this directory. The highest threat from this vulnerability is to data confidentiality and integrity.

## References
- https://github.com/JLLeitschuh/security-research/security/advisories/GHSA-7gf3-89f6-823j
- https://nvd.nist.gov/vuln/detail/CVE-2021-20202
- https://bugzilla.redhat.com/show_bug.cgi?id=1922128
- https://issues.redhat.com/browse/KEYCLOAK-17000
