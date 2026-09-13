# [C] s390/checksum: Fix csum_partial() without vector facility

## Summary
Severity: Critical
Advisory: CVE-2026-68385
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68385
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/checksum: Fix csum_partial() without vector facility

Currently csum_partial() calls csum_copy() with copy=false and dst=NULL.
On machines without the vector facility, csum_copy() falls back to
cksm(dst, ...), causing the checksum to be calculated from address zero
instead of the source buffer.

The VX implementation already checksums data loaded from src. Make the
fallback do the same by passing src to cksm().

## References
- https://git.kernel.org/stable/c/1d9a2f01b3c4e5c88e06b2db4b5460c2ec884722
- https://git.kernel.org/stable/c/4bb06b60d982355e22647b3d12d6619419f8c1fa
- https://git.kernel.org/stable/c/5fc0a2a6eeb99cac991242bb48796c7749ce3261
- https://git.kernel.org/stable/c/898bb2814f38399108bdd2113f38d97383a7036a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68385.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68385
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
