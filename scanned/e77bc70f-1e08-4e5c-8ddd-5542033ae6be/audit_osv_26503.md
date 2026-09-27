# [M] drm/msm/dpu: check for null return of devm_kzalloc() in dpu_writeback_init()

## Summary
Severity: Medium
Advisory: CVE-2023-53284
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53284
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/dpu: check for null return of devm_kzalloc() in dpu_writeback_init()

Because of the possilble failure of devm_kzalloc(), dpu_wb_conn might
be NULL and will cause null pointer dereference later.

Therefore, it might be better to check it and directly return -ENOMEM.

Patchwork: https://patchwork.freedesktop.org/patch/512277/
[DB: fixed typo in commit message]

## References
- https://git.kernel.org/stable/c/21e9a838f505178e109ccb3bf19d7808eb0326f4
- https://git.kernel.org/stable/c/3723c4dbcd14cc96771000ce0b0540801e6ba059
- https://git.kernel.org/stable/c/5ee51b19855c5dd72aca57b8014f3b70d7798733
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53284.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53284
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
