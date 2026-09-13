# [M] CVE-2019-10156

## Summary
Severity: Medium
Advisory: CVE-2019-10156
Aliases: GHSA-grgm-pph5-j5h7, PYSEC-2019-2
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2019-07-30
Source: https://osv.dev/vulnerability/CVE-2019-10156
Type: osv

## Details
A flaw was discovered in the way Ansible templating was implemented in versions before 2.6.18, 2.7.12 and 2.8.2, causing the possibility of information disclosure through unexpected variable substitution. By taking advantage of unintended variable substitution the content of any variable may be disclosed.

## References
- https://access.redhat.com/errata/RHSA-2019:3744
- https://access.redhat.com/errata/RHSA-2019:3789
- https://lists.debian.org/debian-lts-announce/2019/09/msg00016.html
- https://lists.debian.org/debian-lts-announce/2021/01/msg00023.html
- https://www.debian.org/security/2021/dsa-4950
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10156
- https://github.com/ansible/ansible/pull/57188
