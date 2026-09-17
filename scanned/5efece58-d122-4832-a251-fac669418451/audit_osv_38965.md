# [H] drm/amdkfd: Fix out-of-bounds write in kfd_event_page_set()

## Summary
Severity: High
Advisory: CVE-2026-43206
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43206
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: Fix out-of-bounds write in kfd_event_page_set()

The kfd_event_page_set() function writes KFD_SIGNAL_EVENT_LIMIT * 8
bytes via memset without checking the buffer size parameter. This allows
unprivileged userspace to trigger an out-of bounds kernel memory write
by passing a small buffer, leading to  potential privilege
escalation.

## References
- https://git.kernel.org/stable/c/3e04bc310d80b46eaf481f1fefcbcb37a187412d
- https://git.kernel.org/stable/c/4857c37c7ba9aa38b9a4c694e8bd8d0091c87940
- https://git.kernel.org/stable/c/4e72f419e4ed44cb3b60506752d8688c20a60a9b
- https://git.kernel.org/stable/c/75fb57efdd7863fffbc39db23e9cad7aafda26ed
- https://git.kernel.org/stable/c/8a70a26c9f34baea6c3199a9862ddaff4554a96d
- https://git.kernel.org/stable/c/b4034442cb090e4a980bdcc1540948606cbc951b
- https://git.kernel.org/stable/c/bfcd6b53e1f4feb182952f4ff9a137c36ceaf20b
- https://git.kernel.org/stable/c/de8d7a25cd2eb5875b1d8d4fbc7fe4b4138b781f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43206.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43206
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
