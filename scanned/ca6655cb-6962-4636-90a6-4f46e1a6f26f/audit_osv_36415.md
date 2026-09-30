# [H] mtd: rawnand: serialize lock/unlock against other NAND operations

## Summary
Severity: High
Advisory: CVE-2026-23434
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23434
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mtd: rawnand: serialize lock/unlock against other NAND operations

nand_lock() and nand_unlock() call into chip->ops.lock_area/unlock_area
without holding the NAND device lock. On controllers that implement
SET_FEATURES via multiple low-level PIO commands, these can race with
concurrent UBI/UBIFS background erase/write operations that hold the
device lock, resulting in cmd_pending conflicts on the NAND controller.

Add nand_get_device()/nand_release_device() around the lock/unlock
operations to serialize them against all other NAND controller access.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/28ea836cc44cb8b89c1c174707ead0c1133c60e9
- https://git.kernel.org/stable/c/5fd5c078af23cb353507aa522e09d557d7eaef04
- https://git.kernel.org/stable/c/a80291e577b44593a724d6cd64c14337c78f194d
- https://git.kernel.org/stable/c/bab2bc6e850a697a23b9e5f0e21bb8c187615e95
- https://git.kernel.org/stable/c/ce5229e78078e437704157eb542f43a6f83b429b
- https://git.kernel.org/stable/c/f25446e2c28939753d3b62d34dfda49952b2557d
- https://git.kernel.org/stable/c/f71ce0ae5aefe39dd5b2f996c0e08550d2153ad2
- https://git.kernel.org/stable/c/fe4a73c3dd48308149d57a10c2761e1d36ced7ba
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23434.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23434
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
