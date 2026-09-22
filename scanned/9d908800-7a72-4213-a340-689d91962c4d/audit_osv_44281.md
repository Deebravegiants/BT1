# [H] of: reserved_mem: prevent OOB when too many dynamic regions are defined

## Summary
Severity: High
Advisory: CVE-2026-80723
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80723
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.103, >=6.13.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

of: reserved_mem: prevent OOB when too many dynamic regions are defined

On boot, fdt_scan_reserved_mem() saves each dynamically-placed
/reserved-memory subnode into a local array of size
MAX_RESERVED_REGIONS.

If the device tree defines more than MAX_RESERVED_REGIONS
dynamically-placed regions, fdt_scan_reserved_mem() writes past the
end of the local array.

Add a bounds check that logs an error and skips the excess regions,
restoring the original behavior.

## References
- https://git.kernel.org/stable/c/68d27250c9e81ab7764603e346c2b1017cb53adf
- https://git.kernel.org/stable/c/cfa7e2734877330d6c10e0f33953905486c4530c
- https://git.kernel.org/stable/c/db3dbdfea1b8f38774419c5c2c14e4b81c48708d
- https://git.kernel.org/stable/c/de8ccbd6bf4efe7a059e2c483789936009e10f42
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80723.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80723
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
