# [H] CVE-2019-15728

## Summary
Severity: High
Advisory: CVE-2019-15728
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-09-16
Source: https://osv.dev/vulnerability/CVE-2019-15728
Type: osv

## Details
An issue was discovered in GitLab Community and Enterprise Edition 10.1 through 12.2.1. Protections against SSRF attacks on the Kubernetes integration are insufficient, which could have allowed an attacker to request any local network resource accessible from the GitLab server.

## References
- https://about.gitlab.com/2019/08/29/security-release-gitlab-12-dot-2-dot-3-released/
- https://gitlab.com/gitlab-org/gitlab-ce/issues/61314
