# [H] scsi: mpi3mr: Fix issues in mpi3mr_get_all_tgt_info()

## Summary
Severity: High
Advisory: CVE-2023-53320
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53320
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: mpi3mr: Fix issues in mpi3mr_get_all_tgt_info()

The function mpi3mr_get_all_tgt_info() has four issues:

1) It calculates valid entry length in alltgt_info assuming the header part
   of the struct mpi3mr_device_map_info would equal to sizeof(u32).  The
   correct size is sizeof(u64).

2) When it calculates the valid entry length kern_entrylen, it excludes one
   entry by subtracting 1 from num_devices.

3) It copies num_device by calling memcpy(). Substitution is enough.

4) It does not specify the calculated length to sg_copy_from_buffer().
   Instead, it specifies the payload length which is larger than the
   alltgt_info size. It causes "BUG: KASAN: slab-out-of-bounds".

Fix the issues by using the correct header size, removing the subtraction
from num_devices, replacing the memcpy() with substitution and specifying
the correct length to sg_copy_from_buffer().

## References
- https://git.kernel.org/stable/c/2f3d3fa5b8ed7d3b147478f42b00b468eeb1ecd2
- https://git.kernel.org/stable/c/8ba997b22f2cd5d29aad8c39f6201f7608ed0c04
- https://git.kernel.org/stable/c/fb428a2005fc1260d18b989cc5199f281617f44d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53320.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53320
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
