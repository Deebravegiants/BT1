# [M] CVE-2020-1746

## Summary
Severity: Medium
Advisory: CVE-2020-1746
Aliases: GHSA-j2h6-73x8-22c4, PYSEC-2020-13
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2020-05-12
Source: https://osv.dev/vulnerability/CVE-2020-1746
Type: osv

## Details
A flaw was found in the Ansible Engine affecting Ansible Engine versions 2.7.x before 2.7.17 and 2.8.x before 2.8.11 and 2.9.x before 2.9.7 as well as Ansible Tower before and including versions 3.4.5 and 3.5.5 and 3.6.3 when the ldap_attr and ldap_entry community modules are used. The issue discloses the LDAP bind password to stdout or a log file if a playbook task is written using the bind_pw in the parameters field. The highest threat from this vulnerability is data confidentiality.

## References
- https://www.debian.org/security/2021/dsa-4950
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1746
- https://github.com/ansible/ansible/pull/67866
