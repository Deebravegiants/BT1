# [M] Jenkins Kryptowire Plugin vulnerability stores unencrypted Kryptowire API key

## Summary
Severity: Medium
Advisory: GHSA-cvg7-767r-w3fq
CVE: CVE-2025-53672
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-cvg7-767r-w3fq
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:kryptowire` — affected >=0

## Details
Jenkins Kryptowire Plugin 0.2 and earlier stores the Kryptowire API key unencrypted in its global configuration file `org.aerogear.kryptowire.GlobalConfigurationImpl.xml` on the Jenkins controller as part of its configuration.

This API key can be viewed by users with access to the Jenkins controller file system.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53672
- https://github.com/jenkinsci/kryptowire-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3525
- http://www.openwall.com/lists/oss-security/2025/07/09/4
