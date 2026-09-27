# [M] Jenkins Warnings Plugin exposures system-scoped credentials

## Summary
Severity: Medium
Advisory: GHSA-66hv-fhcm-7xm7
CVE: CVE-2023-46651
CWE: CWE-200, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-10-25
Source: https://github.com/advisories/GHSA-66hv-fhcm-7xm7
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:warnings-ng` — affected >=10.5.0 <10.5.1
- Maven: `io.jenkins.plugins:warnings-ng` — affected >=0 <10.4.1

## Details
Jenkins Warnings Plugin 10.5.0 and earlier does not set the appropriate context for credentials lookup, allowing the use of system-scoped credentials otherwise reserved for the global configuration.

This allows attackers with Item/Configure permission to access and capture credentials they are not entitled to.

Warnings Plugin 10.5.1 defines the appropriate context for credentials lookup. This fix has been backported to 10.4.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46651
- https://github.com/jenkinsci/warnings-ng-plugin/commit/17d18d2fae58f5658a40d03a03f927819eb6cf1a
- https://github.com/jenkinsci/warnings-ng-plugin/commit/372cd40ce73b25d8ae632b262f6ae1cd36ad9e4c
- https://github.com/jenkinsci/warnings-ng-plugin
- https://www.jenkins.io/security/advisory/2023-10-25/#SECURITY-3265
- http://www.openwall.com/lists/oss-security/2023/10/25/2
