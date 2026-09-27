# [M] drm/amdkfd: Check for potential null return of kmalloc_array()

## Summary
Severity: Medium
Advisory: CVE-2022-49055
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49055
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <4.9.311, >=4.10.0 <4.14.276, >=4.15.0 <4.19.239, >=4.20.0 <5.4.190, >=5.5.0 <5.10.112, >=5.11.0 <5.15.35, >=5.16.0 <5.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: Check for potential null return of kmalloc_array()

As the kmalloc_array() may return null, the 'event_waiters[i].wait' would lead to null-pointer dereference.
Therefore, it is better to check the return value of kmalloc_array() to avoid this confusion.

## References
- https://git.kernel.org/stable/c/0a692c625e373fef692ffbc7fc41f8a025f01cb7
- https://git.kernel.org/stable/c/1d7a5aae884ca727d41c7ed15d4c82fdb67c040c
- https://git.kernel.org/stable/c/32cf90a521dcc0f136db7ee5ba32bfe5f79e460e
- https://git.kernel.org/stable/c/40bf32dbfef866c83a3e74800b81d79e52b6d20b
- https://git.kernel.org/stable/c/94869bb0de69a812f70231b0eb480bb2f7ae73a6
- https://git.kernel.org/stable/c/c7a268b33882d5feaafd29c1734456f41ba41396
- https://git.kernel.org/stable/c/ebbb7bb9e80305820dc2328a371c1b35679f2667
- https://git.kernel.org/stable/c/f2658d5966bcee8c3eb487875f459756d4f7cdfc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49055.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49055
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
