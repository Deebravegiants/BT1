# [H] drm/amdkfd: Fix buffer overflow in SDMA queue checkpoint/restore on GFX11

## Summary
Severity: High
Advisory: CVE-2026-53143
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53143
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: Fix buffer overflow in SDMA queue checkpoint/restore on GFX11

The v11 MQD manager incorrectly assigned the CP-compute variants of
checkpoint_mqd/restore_mqd for KFD_MQD_TYPE_SDMA queues. These functions
use sizeof(struct v11_compute_mqd) (2048 bytes) instead of sizeof(struct
v11_sdma_mqd) (512 bytes), causing a 1536-byte overflow.

During CRIU checkpoint of an SDMA queue on Navi3x:
- checkpoint_mqd() reads 2048 bytes from a 512-byte SDMA MQD buffer,
  leaking 1536 bytes of adjacent GTT memory to userspace

During CRIU restore:
- restore_mqd() writes 2048 bytes into a 512-byte SDMA MQD buffer,
  corrupting 1536 bytes of adjacent GTT memory (often the ring buffer
  or neighboring MQDs)

This is a copy-paste regression unique to v11. All other ASIC backends
(cik, vi, v9, v10, v12) correctly use the SDMA-specific variants.

Add checkpoint_mqd_sdma() and restore_mqd_sdma() functions that properly
handle the smaller v11_sdma_mqd structure, matching the pattern used in
other MQD managers.

(cherry picked from commit 6fa41db7ffdec97d62433adf03b7b9b759af8c2c)

## References
- https://git.kernel.org/stable/c/16dad1fb0d783a4008de30e32d0038c393de05b1
- https://git.kernel.org/stable/c/2c5b66c9b4057b385566940935ebc32f6e6ebfd2
- https://git.kernel.org/stable/c/352ea59028ea48a6fff77f19ae28f98f71946a80
- https://git.kernel.org/stable/c/d02f05d30f35b036f7cbaf72de634affb5b38ec6
- https://git.kernel.org/stable/c/d3efcadfe3eea5b4263b8f2d4463b15c9fc46a64
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53143.json
- https://access.redhat.com/errata/RHSA-2026:57251
- https://access.redhat.com/errata/RHSA-2026:57252
- https://access.redhat.com/security/cve/CVE-2026-53143
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53143.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53143
- https://bugzilla.redhat.com/show_bug.cgi?id=2492719
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
