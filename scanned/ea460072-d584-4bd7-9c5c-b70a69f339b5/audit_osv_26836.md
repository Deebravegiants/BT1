# [H] hfs/hfsplus: avoid WARN_ON() for sanity check, use proper error handling

## Summary
Severity: High
Advisory: CVE-2023-54130
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54130
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.0.19, >=6.1.0 <6.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

hfs/hfsplus: avoid WARN_ON() for sanity check, use proper error handling

Commit 55d1cbbbb29e ("hfs/hfsplus: use WARN_ON for sanity check") fixed
a build warning by turning a comment into a WARN_ON(), but it turns out
that syzbot then complains because it can trigger said warning with a
corrupted hfs image.

The warning actually does warn about a bad situation, but we are much
better off just handling it as the error it is.  So rather than warn
about us doing bad things, stop doing the bad things and return -EIO.

While at it, also fix a memory leak that was introduced by an earlier
fix for a similar syzbot warning situation, and add a check for one case
that historically wasn't handled at all (ie neither comment nor
subsequent WARN_ON).

## References
- https://git.kernel.org/stable/c/45917be9f0af339a45b4619f31c902d37b8aed59
- https://git.kernel.org/stable/c/82725be426bce0a425cc5e26fbad61ffd29cff03
- https://git.kernel.org/stable/c/90e019006644dad35862cb4aa270f561b0732066
- https://git.kernel.org/stable/c/be01f35efa876eb81cebab2cb0add068b7280ef4
- https://git.kernel.org/stable/c/cb7a95af78d29442b8294683eca4897544b8ef46
- https://git.kernel.org/stable/c/cc2164ada548addfa8ee215196661c3afe0c5154
- https://git.kernel.org/stable/c/da23752d9660ba7a8ca6c5768fd8776f67f59ee7
- https://git.kernel.org/stable/c/f10defb0be6ac42fb6a97b45920d32da6bd6fde8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54130.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54130
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
