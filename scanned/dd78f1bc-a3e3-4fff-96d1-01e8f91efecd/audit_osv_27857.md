# [H] block: Fix iterating over an empty bio with bio_for_each_folio_all

## Summary
Severity: High
Advisory: CVE-2024-26632
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-18
Source: https://osv.dev/vulnerability/CVE-2024-26632
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.75, >=6.2.0 <6.6.14, >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

block: Fix iterating over an empty bio with bio_for_each_folio_all

If the bio contains no data, bio_first_folio() calls page_folio() on a
NULL pointer and oopses.  Move the test that we've reached the end of
the bio from bio_next_folio() to bio_first_folio().

[axboe: add unlikely() to error case]

## References
- https://git.kernel.org/stable/c/7bed6f3d08b7af27b7015da8dc3acf2b9c1f21d7
- https://git.kernel.org/stable/c/a6bd8182137a12d22d3f2cee463271bdcb491659
- https://git.kernel.org/stable/c/c6350b5cb78e9024c49eaee6fdb914ad2903a5fe
- https://git.kernel.org/stable/c/ca3ede3f5893e2d26d4dbdef1eec28a8487fafde
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26632.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26632
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
