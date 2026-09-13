# [H] drm/xe/uapi: Reject coh_none PAT index for CPU cached memory in madvise

## Summary
Severity: High
Advisory: CVE-2026-46309
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-46309
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.32, >=6.19.0 <7.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/uapi: Reject coh_none PAT index for CPU cached memory in madvise

Add validation in xe_vm_madvise_ioctl() to reject PAT indices with
XE_COH_NONE coherency mode when applied to CPU cached memory.

Using coh_none with CPU cached buffers is a security issue. When the
kernel clears pages before reallocation, the clear operation stays in
CPU cache (dirty). GPU with coh_none can bypass CPU caches and read
stale sensitive data directly from DRAM, potentially leaking data from
previously freed pages of other processes.

This aligns with the existing validation in vm_bind path
(xe_vm_bind_ioctl_validate_bo).

v2(Matthew brost)
- Add fixes
- Move one debug print to better place

v3(Matthew Auld)
- Should be drm/xe/uapi
- More Cc

v4(Shuicheng Lin)
- Fix kmem leak issues by the way

v5
- Remove kmem leak because it has been merged by another patch

v6
- Remove the fix which is not related to current fix

v7
- No change

v8
- Rebase

v9
- Limit the restrictions to iGPU

v10
- No change

(cherry picked from commit 016ccdb674b8c899940b3944952c96a6a490d10a)

## References
- https://git.kernel.org/stable/c/4e5591c2fc1b30f4ea5e2eab4c3a695acc404e39
- https://git.kernel.org/stable/c/87f9b1528e1ffc1da3615d552c9a06aba5e20b00
- https://git.kernel.org/stable/c/fea04cf6f2345bc50f15b6638906c35962b89424
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46309.json
- https://access.redhat.com/security/cve/CVE-2026-46309
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46309.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46309
- https://bugzilla.redhat.com/show_bug.cgi?id=2486468
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
