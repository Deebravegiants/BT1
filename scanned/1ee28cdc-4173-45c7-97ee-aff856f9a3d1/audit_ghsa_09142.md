# [H] Jenkins Pipeline: Groovy Libraries Plugin does not prohibit symbolic links in shared libraries

## Summary
Severity: High
Advisory: GHSA-qjq3-wqj5-g37q
CVE: CVE-2026-48921
CWE: CWE-59
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-qjq3-wqj5-g37q
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:pipeline-groovy-lib` — affected >=0 <798.v5cc688825312

## Details
Jenkins Pipeline: Groovy Libraries Plugin 797.v90ea_a_9b_e45a_0 and earlier does not prohibit symbolic links in shared libraries.

This allows attackers able to control the content of a library used by a Pipeline job to read arbitrary files on the Jenkins controller filesystem.

Pipeline: Groovy Libraries Plugin 798.v5cc688825312 prohibits symbolic links in shared libraries.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-48921
- https://github.com/jenkinsci/pipeline-groovy-lib-plugin
- https://www.jenkins.io/security/advisory/2026-05-27/#SECURITY-3727
