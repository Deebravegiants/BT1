# [H] drm/xe: Don't free job in TDR

## Summary
Severity: High
Advisory: CVE-2024-50149
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50149
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe: Don't free job in TDR

Freeing job in TDR is not safe as TDR can pass the run_job thread
resulting in UAF. It is only safe for free job to naturally be called by
the scheduler. Rather free job in TDR, add to pending list.

(cherry picked from commit ea2f6a77d0c40d97f4a4dc93fee4afe15d94926d)

## References
- https://git.kernel.org/stable/c/82926f52d7a09c65d916c0ef8d4305fc95d68c0c
- https://git.kernel.org/stable/c/be8fe75e57f8fa3f87e3b1c283cc7cd9f9b80867
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50149.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50149
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
