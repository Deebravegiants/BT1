# [M] CVE-2019-3828

## Summary
Severity: Medium
Advisory: CVE-2019-3828
Aliases: GHSA-74vq-h4q8-x6jv, PYSEC-2019-5
CVSS: 4.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-03-27
Source: https://osv.dev/vulnerability/CVE-2019-3828
Type: osv

## Details
Ansible fetch module before versions 2.5.15, 2.6.14, 2.7.8 has a path traversal vulnerability which allows copying and overwriting files outside of the specified destination in the local ansible controller host, by not restricting an absolute path.

## References
- http://packetstormsecurity.com/files/172837/Ansible-Fetch-Path-Traversal.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00077.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00020.html
- https://access.redhat.com/errata/RHSA-2019:3744
- https://access.redhat.com/errata/RHSA-2019:3789
- https://usn.ubuntu.com/4072-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3828
- https://github.com/ansible/ansible/pull/52133
