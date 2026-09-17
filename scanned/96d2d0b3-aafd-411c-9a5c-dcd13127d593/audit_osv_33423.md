# [H] smb: client: fix potential UAF in smb2_close_cached_fid()

## Summary
Severity: High
Advisory: CVE-2025-40328
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2025-40328
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.6.117, >=6.7.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix potential UAF in smb2_close_cached_fid()

find_or_create_cached_dir() could grab a new reference after kref_put()
had seen the refcount drop to zero but before cfid_list_lock is acquired
in smb2_close_cached_fid(), leading to use-after-free.

Switch to kref_put_lock() so cfid_release() is called with
cfid_list_lock held, closing that gap.

## References
- https://git.kernel.org/stable/c/065bd62412271a2d734810dd50336cae88c54427
- https://git.kernel.org/stable/c/734e99623c5b65bf2c03e35978a0b980ebc3c2f8
- https://git.kernel.org/stable/c/bdb596ceb4b7c3f28786a33840263728217fbcf5
- https://git.kernel.org/stable/c/cb52d9c86d70298de0ab7c7953653898cbc0efd6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40328.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40328
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
