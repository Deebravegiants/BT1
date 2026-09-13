# [H] s390/vfio_ccw: Move cp cleanup out of not operational

## Summary
Severity: High
Advisory: CVE-2026-80549
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80549
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.185, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/vfio_ccw: Move cp cleanup out of not operational

The fsm_notoper() routine is called when the device has been
lost, and is (by definition) no longer operational. Since this
can happen asynchronously from the normal behavior of the
driver, the cleanup may happen when holding other locks
in the calling sequence (notably, the cio subchannel lock).

Push the cleanup of the private->cp resources to a workqueue,
where it can be done out from under that lock sequence and
a future patch can safely manage the locking requirements.

## References
- https://git.kernel.org/stable/c/0c11f61a876ed6fcca53d442ed3f33ea8362a0f9
- https://git.kernel.org/stable/c/4e3301e2a651d742c05914f6074a25b8e41bce19
- https://git.kernel.org/stable/c/56100baa0eb7055b1026dfa73e696e8066ff71fd
- https://git.kernel.org/stable/c/af1759d8e6e6da9ba94f30a2f92546f406899aa7
- https://git.kernel.org/stable/c/c9b85aa2cf73ea645e55e2c2670e0ddebfe1589b
- https://git.kernel.org/stable/c/f98a9890ca42f4223d2d4c50e0660af3e012fcb4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80549.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80549
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
