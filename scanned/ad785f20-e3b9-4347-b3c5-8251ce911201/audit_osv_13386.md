# [M] CVE-2018-19583

## Summary
Severity: Medium
Advisory: CVE-2018-19583
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-10
Source: https://osv.dev/vulnerability/CVE-2018-19583
Type: osv

## Details
GitLab CE/EE, versions 8.0 up to 11.x before 11.3.11, 11.4 before 11.4.8, and 11.5 before 11.5.1, would log access tokens in the Workhorse logs, permitting administrators with access to the logs to see another user's token.

## References
- http://www.securityfocus.com/bid/109166
- https://about.gitlab.com/2018/11/28/security-release-gitlab-11-dot-5-dot-1-released/
- https://gitlab.com/gitlab-org/gitlab-workhorse/issues/182
