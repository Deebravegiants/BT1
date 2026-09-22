# [M] CVE-2020-1733

## Summary
Severity: Medium
Advisory: CVE-2020-1733
Aliases: GHSA-g4mq-6fp5-qwcf, PYSEC-2020-5
CVSS: 5.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:L)
Published: 2020-03-11
Source: https://osv.dev/vulnerability/CVE-2020-1733
Type: osv

## Details
A race condition flaw was found in Ansible Engine 2.7.17 and prior, 2.8.9 and prior, 2.9.6 and prior when running a playbook with an unprivileged become user. When Ansible needs to run a module with become user, the temporary directory is created in /var/tmp. This directory is created with "umask 77 && mkdir -p <dir>"; this operation does not fail if the directory already exists and is owned by another user. An attacker could take advantage to gain control of the become user as the target directory can be retrieved by iterating '/proc/<pid>/cmdline'.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DKPA4KC3OJSUFASUYMG66HKJE7ADNGFW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MRRYUU5ZBLPBXCYG6CFP35D64NP2UB2S/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WQVOQD4VAIXXTVQAJKTN7NUGTJFE2PCB/
- https://lists.debian.org/debian-lts-announce/2020/05/msg00005.html
- https://security.gentoo.org/glsa/202006-11
- https://www.debian.org/security/2021/dsa-4950
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1733
- https://github.com/ansible/ansible/issues/67791
