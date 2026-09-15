# [H] soundwire: cadence: fix invalid PDI offset

## Summary
Severity: High
Advisory: CVE-2024-38635
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-21
Source: https://osv.dev/vulnerability/CVE-2024-38635
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.278, >=5.5.0 <5.10.219, >=5.11.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

soundwire: cadence: fix invalid PDI offset

For some reason, we add an offset to the PDI, presumably to skip the
PDI0 and PDI1 which are reserved for BPT.

This code is however completely wrong and leads to an out-of-bounds
access. We were just lucky so far since we used only a couple of PDIs
and remained within the PDI array bounds.

A Fixes: tag is not provided since there are no known platforms where
the out-of-bounds would be accessed, and the initial code had problems
as well.

A follow-up patch completely removes this useless offset.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/002364b2d594a9afc0385c09e00994c510b1d089
- https://git.kernel.org/stable/c/2ebcaa0e5db9b6044bb487ae1cf41bc601761567
- https://git.kernel.org/stable/c/4e99103f757cdf636c6ee860994a19a346a11785
- https://git.kernel.org/stable/c/7eeef1e935d23db5265233d92395bd5c648a4021
- https://git.kernel.org/stable/c/8ee1b439b1540ae543149b15a2a61b9dff937d91
- https://git.kernel.org/stable/c/902f6d656441a511ac25c6cffce74496db10a078
- https://git.kernel.org/stable/c/fd4bcb991ebaf0d1813d81d9983cfa99f9ef5328
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38635.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38635
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
