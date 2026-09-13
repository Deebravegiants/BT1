# [H] RDMA/cxgb4: Added NULL check for lookup_atid

## Summary
Severity: High
Advisory: CVE-2024-47749
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47749
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/cxgb4: Added NULL check for lookup_atid

The lookup_atid() function can return NULL if the ATID is
invalid or does not exist in the identifier table, which
could lead to dereferencing a null pointer without a
check in the `act_establish()` and `act_open_rpl()` functions.
Add a NULL check to prevent null pointer dereferencing.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/0d50ae281a1712b9b2ca72830a96b8f11882358d
- https://git.kernel.org/stable/c/39cb9f39913566ec5865581135f3e8123ad1aee1
- https://git.kernel.org/stable/c/4e1fe68d695af367506ea3c794c5969630f21697
- https://git.kernel.org/stable/c/54aaa3ed40972511e423b604324b881425b9ff1e
- https://git.kernel.org/stable/c/b11318dc8a1ec565300bb1a9073095af817cc508
- https://git.kernel.org/stable/c/b12e25d91c7f97958341538c7dc63ee49d01548f
- https://git.kernel.org/stable/c/b9c94c8ba5a713817cffd74c4bacc05187469624
- https://git.kernel.org/stable/c/dd598ac57dcae796cb58551074660c39b43fb155
- https://git.kernel.org/stable/c/e766e6a92410ca269161de059fff0843b8ddd65f
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47749.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47749
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
