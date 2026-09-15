# [H] Script security bypass vulnerability in Jenkins Shared Library Version Override Plugin 

## Summary
Severity: High
Advisory: GHSA-7845-crfj-phc4
CVE: CVE-2024-52554
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-13
Source: https://github.com/advisories/GHSA-7845-crfj-phc4
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:shared-library-version-override` — affected >=0 <19.v3a

## Details
Jenkins Shared Library Version Override Plugin 17.v786074c9fce7 and earlier declares folder-scoped library overrides as trusted, so that they're not executed in the Script Security sandbox, allowing attackers with Item/Configure permission on a folder to configure a folder-scoped library override that runs without sandbox protection. This allows attackers with Item/Configure permission on a folder to configure a folder-scoped library override that runs without sandbox protection. Shared Library Version Override Plugin 19.v3a_c975738d4a_ declares folder-scoped library overrides as untrusted, so that they’re executed in the Script Security sandbox.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-52554
- https://github.com/jenkinsci/shared-library-version-override-plugin
- https://www.jenkins.io/security/advisory/2024-11-13/#SECURITY-3466
