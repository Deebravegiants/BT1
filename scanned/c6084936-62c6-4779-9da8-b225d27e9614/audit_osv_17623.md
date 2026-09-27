# [M] CVE-2020-1753

## Summary
Severity: Medium
Advisory: CVE-2020-1753
Aliases: GHSA-86hp-cj9j-33vv, PYSEC-2020-210
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-03-16
Source: https://osv.dev/vulnerability/CVE-2020-1753
Type: osv

## Details
A security flaw was found in Ansible Engine, all Ansible 2.7.x versions prior to 2.7.17, all Ansible 2.8.x versions prior to 2.8.11 and all Ansible 2.9.x versions prior to 2.9.7, when managing kubernetes using the k8s module. Sensitive parameters such as passwords and tokens are passed to kubectl from the command line, not using an environment variable or an input configuration file. This will disclose passwords and tokens from process list and no_log directive from debug module would not have any effect making these secrets being disclosed on stdout and log files.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DKPA4KC3OJSUFASUYMG66HKJE7ADNGFW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MRRYUU5ZBLPBXCYG6CFP35D64NP2UB2S/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WQVOQD4VAIXXTVQAJKTN7NUGTJFE2PCB/
- https://security.gentoo.org/glsa/202006-11
- https://www.debian.org/security/2021/dsa-4950
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1753
- https://github.com/ansible-collections/kubernetes/pull/51
