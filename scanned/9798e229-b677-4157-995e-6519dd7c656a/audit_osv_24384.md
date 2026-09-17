# [H] UAF in Linux kernel's tcindex (traffic control index filter) implementation

## Summary
Severity: High
Advisory: CVE-2023-1281
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-22
Source: https://osv.dev/vulnerability/CVE-2023-1281
Type: osv

## Details
Use After Free vulnerability in Linux kernel traffic control index filter (tcindex) allows Privilege Escalation. The imperfect hash area can be updated while packets are traversing, which will cause a use-after-free when 'tcf_exts_exec()' is called with the destroyed tcf_ext. A local attacker user can use this vulnerability to elevate its privileges to root.
This issue affects Linux Kernel: from 4.14 before git commit ee059170b1f7e94e55fa6cadee544e176a6e59c2.

## References
- http://www.openwall.com/lists/oss-security/2023/04/11/3
- https://git.kernel.org
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=ee059170b1f7e94e55fa6cadee544e176a6e59c2
- https://kernel.dance/#ee059170b1f7e94e55fa6cadee544e176a6e59c2
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1281.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1281
- https://security.netapp.com/advisory/ntap-20230427-0004/
