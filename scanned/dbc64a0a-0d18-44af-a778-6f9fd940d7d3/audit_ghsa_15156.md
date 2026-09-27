# [M] Shared projects are unconditionally discovered by Jenkins GitLab Branch Source Plugin

## Summary
Severity: Medium
Advisory: GHSA-fw9h-cxx9-gfq3
CVE: CVE-2024-23901
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-01-24
Source: https://github.com/advisories/GHSA-fw9h-cxx9-gfq3
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:gitlab-branch-source` — affected >=0 <688.v5fa

## Details
GitLab allows sharing a project with another group.

Jenkins GitLab Branch Source Plugin 684.vea_fa_7c1e2fe3 and earlier unconditionally discovers projects that are shared with the configured owner group.

This allows attackers to configure and share a project, resulting in a crafted Pipeline being built by Jenkins after the next scan of the group’s projects.

In GitLab Branch Source Plugin 688.v5fa_356ee8520, the default strategy for discovering projects does not discover projects shared with the configured owner group. To discover projects shared with the configured owner group, use the new trait "Discover shared projects".

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23901
- https://github.com/jenkinsci/gitlab-branch-source-plugin/commit/969ccece8e2185ecdb7c342b27173af1ab17045c
- https://github.com/jenkinsci/gitlab-branch-source-plugin
- https://www.jenkins.io/security/advisory/2024-01-24/#SECURITY-3040
- http://www.openwall.com/lists/oss-security/2024/01/24/6
