# [M] Bitbucket OAuth access token exposed in the build log by Bitbucket Branch Source Plugin 

## Summary
Severity: Medium
Advisory: GHSA-x8mf-jcmf-r79f
CVE: CVE-2024-39460
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-06-26
Source: https://github.com/advisories/GHSA-x8mf-jcmf-r79f
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cloudbees-bitbucket-branch-source` — affected >=0 <887.va

## Details
Bitbucket Branch Source Plugin 886.v44cf5e4ecec5 and earlier prints the Bitbucket OAuth access token as part of the Bitbucket URL in the build log in some cases.

Bitbucket Branch Source Plugin 887.va_d359b_3d2d8d does not include the Bitbucket OAuth access token as part of the Bitbucket URL in the build log.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39460
- https://github.com/jenkinsci/bitbucket-branch-source-plugin/commit/ad359b3d2d8d6c114025d81abc59b3c9acb636df
- https://github.com/jenkinsci/bitbucket-branch-source-plugin
- https://www.jenkins.io/security/advisory/2024-06-26/#SECURITY-3363
- http://www.openwall.com/lists/oss-security/2024/06/26/2
