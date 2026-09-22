# [H] staging: media: atomisp: Disallow all private IOCTLs

## Summary
Severity: High
Advisory: CVE-2026-46205
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46205
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <4.18, >=5.8.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.90, >=6.13.0 <6.18.32, >=6.19.0 <7.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: media: atomisp: Disallow all private IOCTLs

Disallow all private IOCTLs. These aren't quite as safe as one could
assume of IOCTL handlers; disable them for now. Instead of removing the
code, return in the beginning of the function if cmd is non-zero in order
to keep static checkers happy.

## References
- https://git.kernel.org/stable/c/2b7eb2c5dc72f0fc954ac4aa155f9e285e937f7c
- https://git.kernel.org/stable/c/51b8dc5163d2ff2bf04019f8bf7e3bd0e75bb654
- https://git.kernel.org/stable/c/64e85679beafe082fc2e70a557ec356c7fd27548
- https://git.kernel.org/stable/c/6850a439f8d23d4979624f1d6880d3118d473a28
- https://git.kernel.org/stable/c/6f1ce75a75c65061e7a720c3d0ee5f8adab7a2d3
- https://git.kernel.org/stable/c/8774f8cb661f57ae43cc3bc0509d16ef1f406e45
- https://git.kernel.org/stable/c/8c7a281a99224a5b9af99c4dcd98d68eea75926c
- https://git.kernel.org/stable/c/c7848b67ef10f581114b6a2f52b160fc20eb52c9
- https://git.kernel.org/stable/c/ceb1b5f910e58986ea544ff8c9c2f23ae9a52414
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46205.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46205
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
