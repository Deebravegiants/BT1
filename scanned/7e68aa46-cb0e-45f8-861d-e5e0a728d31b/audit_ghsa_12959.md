# [M] Jenkins Maven Artifact ChoiceListProvider (Nexus) Plugin vulnerable to exposure of system-scoped credentials

## Summary
Severity: Medium
Advisory: GHSA-97mg-9jhf-r7rm
CVE: CVE-2023-40347
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-08-16
Source: https://github.com/advisories/GHSA-97mg-9jhf-r7rm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:maven-artifact-choicelistprovider` — affected >=0

## Details
Jenkins Maven Artifact ChoiceListProvider (Nexus) Plugin 1.14 and earlier does not set the appropriate context for credentials lookup, allowing the use of System-scoped credentials otherwise reserved for the global configuration.

This allows attackers with Item/Configure permission to access and capture credentials they are not entitled to.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40347
- https://www.jenkins.io/security/advisory/2023-08-16/#SECURITY-3153
- http://www.openwall.com/lists/oss-security/2023/08/16/3
