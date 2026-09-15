# [M] drm/amdgpu: drop redundant sched job cleanup when cs is aborted

## Summary
Severity: Medium
Advisory: CVE-2023-53228
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53228
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.167, >=6.2.0 <6.3.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: drop redundant sched job cleanup when cs is aborted

Once command submission failed due to userptr invalidation in
amdgpu_cs_submit, legacy code will perform cleanup of scheduler
job. However, it's not needed at all, as former commit has integrated
job cleanup stuff into amdgpu_job_free. Otherwise, because of double
free, a NULL pointer dereference will occur in such scenario.

Bug: https://gitlab.freedesktop.org/drm/amd/-/issues/2457

## References
- https://git.kernel.org/stable/c/1253685f0d3eb3eab0bfc4bf15ab341a5f3da0c8
- https://git.kernel.org/stable/c/c1564d4b105ae535eb3183ecaaa987685b20a888
- https://git.kernel.org/stable/c/cdce1644d85e858c68fb5fa67d78eb1035bf34f4
- https://git.kernel.org/stable/c/ec02a29c3c2ef8ad3e15a0e3f96b99a00e5d97b4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53228.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53228
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
