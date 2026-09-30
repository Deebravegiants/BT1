# [M] CVE-2017-17716

## Summary
Severity: Medium
Advisory: CVE-2017-17716
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-12-17
Source: https://osv.dev/vulnerability/CVE-2017-17716
Type: osv

## Details
GitLab 9.4.x before 9.4.2 does not support LDAP SSL certificate verification, but a verify_certificates LDAP option was mentioned in the 9.4 release announcement. This issue occurred because code was not merged. This is related to use of the omniauth-ldap library and the gitlab_omniauth-ldap gem.

## References
- https://about.gitlab.com/2017/07/22/gitlab-9-4-released/#security---add-ldap-ssl-certificate-verification
- https://about.gitlab.com/2017/07/28/gitlab-9-dot-4-dot-2-released/
- https://gitlab.com/gitlab-org/gitlab-ce/issues/30420
