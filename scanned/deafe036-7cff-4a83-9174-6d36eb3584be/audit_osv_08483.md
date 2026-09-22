# [M] CVE-2016-3723

## Summary
Severity: Medium
Advisory: CVE-2016-3723
Aliases: GHSA-8572-5jrg-mx52
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2016-05-17
Source: https://osv.dev/vulnerability/CVE-2016-3723
Type: osv

## Details
Jenkins before 2.3 and LTS before 1.651.2 allow remote authenticated users with read access to obtain sensitive plugin installation information by leveraging missing permissions checks in unspecified XML/JSON API endpoints.

## References
- http://rhn.redhat.com/errata/RHSA-2016-1773.html
- https://access.redhat.com/errata/RHSA-2016:1206
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2016-05-11
- https://www.cloudbees.com/jenkins-security-advisory-2016-05-11
