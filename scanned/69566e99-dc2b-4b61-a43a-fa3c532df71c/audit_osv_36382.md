# [H] accel/amdxdna: Prevent ubuf size overflow

## Summary
Severity: High
Advisory: CVE-2026-23280
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-23280
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.17, >=6.19.0 <6.19.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/amdxdna: Prevent ubuf size overflow

The ubuf size calculation may overflow, resulting in an undersized
allocation and possible memory corruption.

Use check_add_overflow() helpers to validate the size calculation before
allocation.

## References
- https://git.kernel.org/stable/c/03808abb1d868aed7478a11a82e5bb4b3f1ca6d6
- https://git.kernel.org/stable/c/1500b31db94374a6669e73ce94d6f71cf8e85e06
- https://git.kernel.org/stable/c/972bf4a23478fcb247b4f507d47a584bc8aea5bd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23280.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23280
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
