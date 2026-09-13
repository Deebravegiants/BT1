# [H] io_uring/rsrc: don't rely on user vaddr alignment

## Summary
Severity: High
Advisory: CVE-2025-40216
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-40216
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.36, >=6.13.0 <6.15.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/rsrc: don't rely on user vaddr alignment

There is no guaranteed alignment for user pointers, however the
calculation of an offset of the first page into a folio after coalescing
uses some weird bit mask logic, get rid of it.

## References
- https://git.kernel.org/stable/c/3a3c6d61577dbb23c09df3e21f6f9eda1ecd634b
- https://git.kernel.org/stable/c/50998b0ae7d9d552e96d8b7239981cf05f65eff5
- https://git.kernel.org/stable/c/f16769241594be59387b56ab525e327f54377e60
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40216.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40216
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
