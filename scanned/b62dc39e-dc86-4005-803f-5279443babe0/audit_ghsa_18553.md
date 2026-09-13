# [M] Jenkins HTML Publisher Plugin vulnerability displays controller file system information in its logs

## Summary
Severity: Medium
Advisory: GHSA-367v-5ppj-2hrx
CVE: CVE-2025-53651
CWE: CWE-36, CWE-779
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-367v-5ppj-2hrx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:htmlpublisher` — affected >=0 <427

## Details
Jenkins HTML Publisher Plugin 425 and earlier displays log messages that include the absolute paths of files archived during the Publish HTML reports post-build step, exposing information about the Jenkins controller file system in the build log.

HTML Publisher Plugin 427 displays only the parent directory name of files archived during the Publish HTML reports post-build step in its log messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53651
- https://github.com/jenkinsci/htmlpublisher-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3547
- http://www.openwall.com/lists/oss-security/2025/07/09/4
