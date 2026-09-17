# [H] staging: vme_user: bound slave read/write to the kern_buf size

## Summary
Severity: High
Advisory: CVE-2026-64449
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64449
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.32 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: vme_user: bound slave read/write to the kern_buf size

The SLAVE-path helpers buffer_to_user() and buffer_from_user() copy
'count' bytes into/out of the fixed-size kern_buf (size_buf ==
PCI_BUF_SIZE == 0x20000, 128 KiB) using *ppos as the offset, without
bounding *ppos + count against size_buf.

vme_user_write()/vme_user_read() only clamp count to the VME window size
(image_size = vme_get_size(resource)), which VME_SET_SLAVE sets from the
user-supplied slave.size -- validated against the VME address space (up
to VME_A32_MAX = 4 GiB), not against PCI_BUF_SIZE.  When the window
exceeds 128 KiB, a write()/read() copies past the kern_buf allocation.

Clamp count against size_buf in both helpers, with an early return when
*ppos is already at/after the buffer end.  *ppos is >= 0 here (the caller
rejects negative offsets), so size_buf - *ppos cannot wrap.  This mirrors
the existing clamp in the MASTER-path helpers resource_to_user() /
resource_from_user(), and matches the read()/write() convention of a
short transfer at end-of-buffer.

Found by static analysis (CodeQL taint tracking + CBMC bounded model
checking) and confirmed dynamically under KASAN with the vme_fake bridge:

  BUG: KASAN: slab-out-of-bounds in _copy_from_user+0x2d/0x80
  Write of size 262144 at addr ffff888004100000 by task trigger/68
    _copy_from_user+0x2d/0x80
    vme_user_write+0x13e/0x240 [vme_user]
    vfs_write+0x1b8/0x7a0
    ksys_write+0xb8/0x150

## References
- https://git.kernel.org/stable/c/1b495fa0d4927c88d88bf346bf311f2e26e860ed
- https://git.kernel.org/stable/c/65358d89dc9f1c25d9364b2b3ef0f3b47717f9ed
- https://git.kernel.org/stable/c/8eff7cd4817e14dbe3b9952cce55ef52d1d38940
- https://git.kernel.org/stable/c/9f32f38265014fac7f5dc9490fb01a638ce6e121
- https://git.kernel.org/stable/c/adc8b9c30d716c362646edb45662aa1c641a154a
- https://git.kernel.org/stable/c/e99f2df433c63c86c93de1e5f08f16e404388756
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64449.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64449
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
