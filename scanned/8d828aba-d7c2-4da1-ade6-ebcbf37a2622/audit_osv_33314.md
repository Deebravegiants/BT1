# [H] fs: ntfs3: Fix integer overflow in run_unpack()

## Summary
Severity: High
Advisory: CVE-2025-40068
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40068
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.195, >=5.16.0 <6.1.156, >=6.2.0 <6.6.112, >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs: ntfs3: Fix integer overflow in run_unpack()

The MFT record relative to the file being opened contains its runlist,
an array containing information about the file's location on the physical
disk. Analysis of all Call Stack paths showed that the values of the
runlist array, from which LCNs are calculated, are not validated before
run_unpack function.

The run_unpack function decodes the compressed runlist data format
from MFT attributes (for example, $DATA), converting them into a runs_tree
structure, which describes the mapping of virtual clusters (VCN) to
logical clusters (LCN). The NTFS3 subsystem also has a shortcut for
deleting files from MFT records - in this case, the RUN_DEALLOCATE
command is sent to the run_unpack input, and the function logic
provides that all data transferred to the runlist about file or
directory is deleted without creating a runs_tree structure.

Substituting the runlist in the $DATA attribute of the MFT record for an
arbitrary file can lead either to access to arbitrary data on the disk
bypassing access checks to them (since the inode access check
occurs above) or to destruction of arbitrary data on the disk.

Add overflow check for addition operation.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/3ac37e100385b59ac821a62118494442238aaac4
- https://git.kernel.org/stable/c/5aa5799d162ad1b8e8b699d48b6218143c695a78
- https://git.kernel.org/stable/c/736fc7bf5f68f6b74a0925b7e072c571838657d2
- https://git.kernel.org/stable/c/9378cfe228c2c679564a4116bcb28c8e89dff989
- https://git.kernel.org/stable/c/a86c8b9d03f7101e1750233846fe989df6f0d631
- https://git.kernel.org/stable/c/f6b36cfd25cbadad63447c673743cf771090e756
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40068.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40068
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
