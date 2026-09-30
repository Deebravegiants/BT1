# [H] fs/ntfs3: reject index allocation if $BITMAP is empty but blocks exist

## Summary
Severity: High
Advisory: CVE-2025-40067
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40067
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.112, >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: reject index allocation if $BITMAP is empty but blocks exist

Index allocation requires at least one bit in the $BITMAP attribute to
track usage of index entries. If the bitmap is empty while index blocks
are already present, this reflects on-disk corruption.

syzbot triggered this condition using a malformed NTFS image. During a
rename() operation involving a long filename (which spans multiple
index entries), the empty bitmap allowed the name to be added without
valid tracking. Subsequent deletion of the original entry failed with
-ENOENT, due to unexpected index state.

Reject such cases by verifying that the bitmap is not empty when index
blocks exist.

## References
- https://git.kernel.org/stable/c/039ddf353cc33f6546a87ec1ac3210637d714bec
- https://git.kernel.org/stable/c/0dc7117da8f92dd5fe077d712a756eccbe377d40
- https://git.kernel.org/stable/c/978aac54e93ea35aab20b32ae393d3d33964e7ae
- https://git.kernel.org/stable/c/be66551da203862c689c12e1d35ce87217c017c1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40067.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40067
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
