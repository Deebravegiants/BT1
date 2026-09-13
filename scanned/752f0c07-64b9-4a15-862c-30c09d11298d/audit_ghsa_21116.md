# [M] Jenkins Git client plugin 3.11.0 does not perform SSH host key verification

## Summary
Severity: Medium
Advisory: GHSA-cm7j-p8hc-97vj
CVE: CVE-2022-36881
CWE: CWE-295, CWE-322
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-cm7j-p8hc-97vj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:git-client` — affected >=0 <3.11.1

## Details
Jenkins Git client plugin 3.11.0 and earlier does not perform SSH host key verification when connecting to Git repositories via SSH, enabling man-in-the-middle attacks. Git client Plugin 3.11.1 provides strategies for performing host key verification for administrators to select the one that meets their security needs. For more information see [the plugin documentation](https://github.com/jenkinsci/git-client-plugin#ssh-host-key-verification).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36881
- https://github.com/jenkinsci/git-client-plugin/commit/88f52c6c9b18bca4ad210e3b9910a49433583fd9
- https://github.com/jenkinsci/git-client-plugin
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-1468
- http://www.openwall.com/lists/oss-security/2022/07/27/1
