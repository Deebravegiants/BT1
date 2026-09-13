# [H] accel/qaic: Fix integer overflow in qaic_validate_req()

## Summary
Severity: High
Advisory: CVE-2025-22001
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2025-22001
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.85, >=6.7.0 <6.12.21, >=6.13.0 <6.13.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/qaic: Fix integer overflow in qaic_validate_req()

These are u64 variables that come from the user via
qaic_attach_slice_bo_ioctl().  Use check_add_overflow() to ensure that
the math doesn't have an integer wrapping bug.

## References
- https://git.kernel.org/stable/c/4b2a170c25862ad116bd31be6b9841646b4862e8
- https://git.kernel.org/stable/c/57fae0c505f49bb1e3d5660cd2cc49697ed85f7c
- https://git.kernel.org/stable/c/67d15c7aa0864dfd82325c7e7e7d8548b5224c7b
- https://git.kernel.org/stable/c/b362fc904d264a88b4af20baae9e82491c285e9c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22001.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22001
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
