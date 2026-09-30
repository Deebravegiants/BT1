# [H] peci: cpu: Fix use-after-free in adev_release()

## Summary
Severity: High
Advisory: CVE-2022-48670
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2022-48670
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <5.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

peci: cpu: Fix use-after-free in adev_release()

When auxiliary_device_add() returns an error, auxiliary_device_uninit()
is called, which causes refcount for device to be decremented and
.release callback will be triggered.

Because adev_release() re-calls auxiliary_device_uninit(), it will cause
use-after-free:
[ 1269.455172] WARNING: CPU: 0 PID: 14267 at lib/refcount.c:28 refcount_warn_saturate+0x110/0x15
[ 1269.464007] refcount_t: underflow; use-after-free.

## References
- https://git.kernel.org/stable/c/1c11289b34ab67ed080bbe0f1855c4938362d9cf
- https://git.kernel.org/stable/c/c87f1f99e26ea4ae08cabe753ae98e5626bdba89
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48670.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48670
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
