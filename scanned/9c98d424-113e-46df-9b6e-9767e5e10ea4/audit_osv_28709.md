# [H] scsi: sg: Avoid sg device teardown race

## Summary
Severity: High
Advisory: CVE-2024-35954
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-35954
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.28, >=6.7.0 <6.8.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: sg: Avoid sg device teardown race

sg_remove_sfp_usercontext() must not use sg_device_destroy() after calling
scsi_device_put().

sg_device_destroy() is accessing the parent scsi_device request_queue which
will already be set to NULL when the preceding call to scsi_device_put()
removed the last reference to the parent scsi_device.

The resulting NULL pointer exception will then crash the kernel.

## References
- https://git.kernel.org/stable/c/27f58c04a8f438078583041468ec60597841284d
- https://git.kernel.org/stable/c/46af9047523e2517712ae8e71d984286c626e022
- https://git.kernel.org/stable/c/b0d1ebcc1a9560e494ea9b3ee808540db26c5086
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35954.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35954
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
