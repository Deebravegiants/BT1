# [M] Stored XSS vulnerability in Jenkins Git Plugin

## Summary
Severity: Medium
Advisory: GHSA-gghc-g8cj-4vfv
CVE: CVE-2021-21684
CWE: CWE-116, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-gghc-g8cj-4vfv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:git` — affected >=0 <4.8.3

## Details
Jenkins Git Plugin 4.8.2 and earlier does not escape the Git SHA-1 checksum parameters provided to commit notifications when displaying them in a build cause.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to submit crafted commit notifications to the `/git/notifyCommit` endpoint.

Jenkins Git Plugin 4.8.3 rejects Git SHA-1 checksum parameters that do not match the expected format. Existing values are sanitized when displayed on the UI.

This vulnerability is only exploitable in Jenkins 2.314 and earlier, LTS 2.303.1 and earlier. See the [LTS upgrade guide](https://www.jenkins.io/doc/upgrade-guide/2.303/#SECURITY-2452).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21684
- https://github.com/jenkinsci/git-plugin/commit/5474cc942bfba60927be629ff47fb41c38c66741
- https://github.com/jenkinsci/git-plugin
- https://www.jenkins.io/security/advisory/2021-10-06/#SECURITY-2499
- http://www.openwall.com/lists/oss-security/2021/10/06/1
