# [C] CVE-2019-5464

## Summary
Severity: Critical
Advisory: CVE-2019-5464
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-28
Source: https://osv.dev/vulnerability/CVE-2019-5464
Type: osv

## Details
A flawed DNS rebinding protection issue was discovered in GitLab CE/EE 10.2 and later in the `url_blocker.rb` which could result in SSRF where the library is utilized.

## References
- https://hackerone.com/reports/632101
- https://about.gitlab.com/releases/2019/07/29/security-release-gitlab-12-dot-1-dot-2-released/
- https://gitlab.com/gitlab-org/gitlab-ce/issues/63959
