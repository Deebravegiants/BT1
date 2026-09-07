# [H] Jenkins Folders Plugin cross-site request forgery vulnerability

## Summary
Severity: High
Advisory: GHSA-4vqp-pcm3-73xp
CVE: CVE-2023-40336
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-16
Source: https://github.com/advisories/GHSA-4vqp-pcm3-73xp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cloudbees-folder` — affected >=0 <6.848.ve3b

## Details
Jenkins Folders Plugin 6.846.v23698686f0f6 and earlier does not require POST requests for an HTTP endpoint, resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to copy an item, which could potentially automatically approve unsandboxed scripts and allow the execution of unsafe scripts.

Folders Plugin 6.848.ve3b_fd7839a_81 requires POST requests for the affected HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40336
- https://www.jenkins.io/security/advisory/2023-08-16/#SECURITY-3106
- http://www.openwall.com/lists/oss-security/2023/08/16/3
