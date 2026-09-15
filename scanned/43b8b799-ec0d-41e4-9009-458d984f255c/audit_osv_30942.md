# [M] mtd: spinand: winbond: Fix 512GW, 01GW, 01JW and 02JW ECC information

## Summary
Severity: Medium
Advisory: CVE-2024-56771
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2024-56771
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

mtd: spinand: winbond: Fix 512GW, 01GW, 01JW and 02JW ECC information

These four chips:
* W25N512GW
* W25N01GW
* W25N01JW
* W25N02JW
all require a single bit of ECC strength and thus feature an on-die
Hamming-like ECC engine. There is no point in filling a ->get_status()
callback for them because the main ECC status bytes are located in
standard places, and retrieving the number of bitflips in case of
corrected chunk is both useless and unsupported (if there are bitflips,
then there is 1 at most, so no need to query the chip for that).

Without this change, a kernel warning triggers every time a bit flips.

## References
- https://git.kernel.org/stable/c/234d5f75c3ae911b52c5e4442b8a87fbbd129836
- https://git.kernel.org/stable/c/fee9b240916df82a8b07aef0fdfe96785417a164
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56771.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56771
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
