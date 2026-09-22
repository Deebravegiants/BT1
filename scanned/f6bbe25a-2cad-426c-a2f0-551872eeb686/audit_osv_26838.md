# [H] maple_tree: fix potential out-of-bounds access in mas_wr_end_piv()

## Summary
Severity: High
Advisory: CVE-2023-54135
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54135
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.37, >=6.2.0 <6.3.11, >=6.4.0 <6.4.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

maple_tree: fix potential out-of-bounds access in mas_wr_end_piv()

Check the write offset end bounds before using it as the offset into the
pivot array.  This avoids a possible out-of-bounds access on the pivot
array if the write extends to the last slot in the node, in which case the
node maximum should be used as the end pivot.

akpm: this doesn't affect any current callers, but new users of mapletree
may encounter this problem if backported into earlier kernels, so let's
fix it in -stable kernels in case of this.

## References
- https://git.kernel.org/stable/c/4e2ad53ababeaac44d71162650984abfe783960c
- https://git.kernel.org/stable/c/cd00dd2585c4158e81fdfac0bbcc0446afbad26d
- https://git.kernel.org/stable/c/dc4751bd4aba01ccfc02f91adfeee0ba4cda405c
- https://git.kernel.org/stable/c/f5fcf6555a2a4f32947d17b92b173837cc652891
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54135.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54135
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
