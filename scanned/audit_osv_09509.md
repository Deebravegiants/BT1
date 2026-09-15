# [M] CVE-2017-0920

## Summary
Severity: Medium
Advisory: CVE-2017-0920
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-03-22
Source: https://osv.dev/vulnerability/CVE-2017-0920
Type: osv

## Details
GitLab Community and Enterprise Editions before 10.1.6, 10.2.6, and 10.3.4 are vulnerable to an authorization bypass issue in the Projects::MergeRequests::CreationsController component resulting in an attacker to see every project name and their respective namespace on a GitLab instance.

## References
- https://about.gitlab.com/2018/01/16/gitlab-10-dot-3-dot-4-released/
- https://www.debian.org/security/2018/dsa-4206
- https://hackerone.com/reports/301336
