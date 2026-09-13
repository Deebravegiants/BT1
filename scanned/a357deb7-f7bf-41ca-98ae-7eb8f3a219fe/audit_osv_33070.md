# [H] iommufd: Prevent ALIGN() overflow

## Summary
Severity: High
Advisory: CVE-2025-38688
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-09-04
Source: https://osv.dev/vulnerability/CVE-2025-38688
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.103, >=6.7.0 <6.12.43, >=6.13.0 <6.15.11, >=6.16.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommufd: Prevent ALIGN() overflow

When allocating IOVA the candidate range gets aligned to the target
alignment. If the range is close to ULONG_MAX then the ALIGN() can
wrap resulting in a corrupted iova.

Open code the ALIGN() using get_add_overflow() to prevent this.
This simplifies the checks as we don't need to check for length earlier
either.

Consolidate the two copies of this code under a single helper.

This bug would allow userspace to create a mapping that overlaps with some
other mapping or a reserved range.

## References
- https://git.kernel.org/stable/c/79fad1917802c28de51a479318a056a6fbe3e2f2
- https://git.kernel.org/stable/c/b42497e3c0e74db061eafad41c0cd7243c46436b
- https://git.kernel.org/stable/c/d19b817540c0abe84854a64ee9ee34cecc3bbeef
- https://git.kernel.org/stable/c/e42a046bb41dcdde4f766a17d8211842007ed537
- https://git.kernel.org/stable/c/ebb6021560b94649bec6b8faba6fe0dca2218e81
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38688.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38688
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
