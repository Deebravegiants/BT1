# [H] Use-after-free in tcindex (traffic control index filter) in the Linux Kernel

## Summary
Severity: High
Advisory: CVE-2023-1829
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-12
Source: https://osv.dev/vulnerability/CVE-2023-1829
Type: osv

## Details
A use-after-free vulnerability in the Linux Kernel traffic control index filter (tcindex) can be exploited to achieve local privilege escalation. The tcindex_delete function which does not properly deactivate filters in case of a perfect hashes while deleting the underlying structure which can later lead to double freeing the structure. A local attacker user can use this vulnerability to elevate its privileges to root.
We recommend upgrading past commit 8c710f75256bb3cf05ac7b1672c82b92c43f3d28.

## References
- https://git.kernel.org
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=8c710f75256bb3cf05ac7b1672c82b92c43f3d28
- https://kernel.dance/#8c710f75256bb3cf05ac7b1672c82b92c43f3d28
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1829.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1829
- https://security.netapp.com/advisory/ntap-20230601-0001/
