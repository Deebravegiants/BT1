# [H] CVE-2019-14904

## Summary
Severity: High
Advisory: CVE-2019-14904
Aliases: GHSA-gwr8-5j83-483c, PYSEC-2020-161
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:L/A:L)
Published: 2020-08-26
Source: https://osv.dev/vulnerability/CVE-2019-14904
Type: osv

## Details
A flaw was found in the solaris_zone module from the Ansible Community modules. When setting the name for the zone on the Solaris host, the zone name is checked by listing the process with the 'ps' bare command on the remote machine. An attacker could take advantage of this flaw by crafting the name of the zone and executing arbitrary commands in the remote host. Ansible Engine 2.7.15, 2.8.7, and 2.9.2 as well as previous versions are affected.

## References
- https://lists.debian.org/debian-lts-announce/2021/01/msg00023.html
- https://www.debian.org/security/2021/dsa-4950
- https://bugzilla.redhat.com/show_bug.cgi?id=1776944
- https://github.com/ansible/ansible/pull/65686
