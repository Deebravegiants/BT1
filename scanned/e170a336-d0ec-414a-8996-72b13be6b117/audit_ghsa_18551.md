# [M] Jenkins Git Parameter Plugin vulnerable to code injection due to inexhaustive parameter check

## Summary
Severity: Medium
Advisory: GHSA-qcj2-99cg-mppf
CVE: CVE-2025-53652
CWE: CWE-1287, CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-qcj2-99cg-mppf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.tools:git-parameter` — affected >=0 <444.vca

## Details
Jenkins Git Parameter Plugin implements a choice build parameter that lists the configured Git SCM’s branches, tags, pull requests, and revisions.

Git Parameter Plugin 439.vb_0e46ca_14534 and earlier does not validate that the Git parameter value submitted to the build matches one of the offered choices.

This allows attackers with Item/Build permission to inject arbitrary values into Git parameters.

Git Parameter Plugin 444.vca_b_84d3703c2 validates that the Git parameter value submitted to the build matches one of the offered choices.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53652
- https://github.com/jenkinsci/git-parameter-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3419
- http://www.openwall.com/lists/oss-security/2025/07/09/4
