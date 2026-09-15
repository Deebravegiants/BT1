# [M] CVE-2016-8647

## Summary
Severity: Medium
Advisory: CVE-2016-8647
Aliases: GHSA-x4cm-m36h-c6qj, PYSEC-2018-58
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-07-26
Source: https://osv.dev/vulnerability/CVE-2016-8647
Type: osv

## Details
An input validation vulnerability was found in Ansible's mysql_user module before 2.2.1.0, which may fail to correctly change a password in certain circumstances. Thus the previous password would still be active when it should have been changed.

## References
- https://access.redhat.com/errata/RHSA-2017:1685
- https://github.com/ansible/ansible-modules-core/pull/5388
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-8647
