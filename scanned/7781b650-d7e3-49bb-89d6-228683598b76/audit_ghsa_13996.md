# [M] Jenkins Code Dx Plugin stores API keys in plain text

## Summary
Severity: Medium
Advisory: GHSA-gpc2-f62m-c6h6
CVE: CVE-2023-2632
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-gpc2-f62m-c6h6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:codedx` — affected >=0 <4.0.0

## Details
Jenkins Code Dx Plugin 3.1.0 and earlier stores Code Dx server API keys unencrypted in job `config.xml` files on the Jenkins controller as part of its configuration.

These API keys can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

Additionally, the job configuration form does not mask these API keys, increasing the potential for attackers to observe and capture them.

Code Dx Plugin 4.0.0 no longer stores the API keys directly, instead accessing them through its newly added Credentials Plugin integration. Affected jobs need to be reconfigured.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2632
- https://github.com/jenkinsci/codedx-plugin/commit/a971a75da3eaf0ab5344c2b60942e7c8809ec913
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-3146
