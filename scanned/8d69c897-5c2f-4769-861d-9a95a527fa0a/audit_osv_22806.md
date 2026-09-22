# [H] Git vulnerable to Remote Code Execution via Heap overflow in `git shell`

## Summary
Severity: High
Advisory: CVE-2022-39260
Aliases: GHSA-rjr6-wcq6-83p6
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-10-19
Source: https://osv.dev/vulnerability/CVE-2022-39260
Type: osv

## Details
Git is an open source, scalable, distributed revision control system. `git shell` is a restricted login shell that can be used to implement Git's push/pull functionality via SSH. In versions prior to 2.30.6, 2.31.5, 2.32.4, 2.33.5, 2.34.5, 2.35.5, 2.36.3, and 2.37.4, the function that splits the command arguments into an array improperly uses an `int` to represent the number of entries in the array, allowing a malicious actor to intentionally overflow the return value, leading to arbitrary heap writes. Because the resulting array is then passed to `execv()`, it is possible to leverage this attack to gain remote code execution on a victim machine. Note that a victim must first allow access to `git shell` as a login shell in order to be vulnerable to this attack. This problem is patched in versions 2.30.6, 2.31.5, 2.32.4, 2.33.5, 2.34.5, 2.35.5, 2.36.3, and 2.37.4 and users are advised to upgrade to the latest version. Disabling `git shell` access via remote logins is a viable short-term workaround.

## References
- https://support.apple.com/kb/HT213496
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39260.json
- https://github.com/git/git/security/advisories/GHSA-rjr6-wcq6-83p6
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/C7B6JPKX5CGGLAHXJVQMIZNNEEB72FHD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OHNO2FB55CPX47BAXMBWUBGWHO6N6ZZH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UKFHE4KVD7EKS5J3KTDFVBEKU3CLXGVV/
- https://nvd.nist.gov/vuln/detail/CVE-2022-39260
- https://security.gentoo.org/glsa/202312-15
- http://seclists.org/fulldisclosure/2022/Nov/1
- https://lists.debian.org/debian-lts-announce/2022/12/msg00025.html
