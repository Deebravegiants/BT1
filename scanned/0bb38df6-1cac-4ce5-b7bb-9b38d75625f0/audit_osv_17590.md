# [M] CVE-2020-1740

## Summary
Severity: Medium
Advisory: CVE-2020-1740
Aliases: GHSA-vcg8-98q8-g7mj, PYSEC-2020-12
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-03-16
Source: https://osv.dev/vulnerability/CVE-2020-1740
Type: osv

## Details
A flaw was found in Ansible Engine when using Ansible Vault for editing encrypted files. When a user executes "ansible-vault edit", another user on the same computer can read the old and new secret, as it is created in a temporary file with mkstemp and the returned file descriptor is closed and the method write_data is called to write the existing secret in the file. This method will delete the file before recreating it insecurely. All versions in 2.7.x, 2.8.x and 2.9.x branches are believed to be vulnerable.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DKPA4KC3OJSUFASUYMG66HKJE7ADNGFW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MRRYUU5ZBLPBXCYG6CFP35D64NP2UB2S/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WQVOQD4VAIXXTVQAJKTN7NUGTJFE2PCB/
- https://lists.debian.org/debian-lts-announce/2020/05/msg00005.html
- https://security.gentoo.org/glsa/202006-11
- https://www.debian.org/security/2021/dsa-4950
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1740
- https://github.com/ansible/ansible/issues/67798
