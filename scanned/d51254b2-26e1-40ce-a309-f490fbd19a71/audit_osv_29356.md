# [H] s390/dasd: Fix invalid dereferencing of indirect CCW data pointer

## Summary
Severity: High
Advisory: CVE-2024-42099
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-42099
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.9.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/dasd: Fix invalid dereferencing of indirect CCW data pointer

Fix invalid dereferencing of indirect CCW data pointer in
dasd_eckd_dump_sense() that leads to a kernel panic in error cases.

When using indirect addressing for DASD CCWs (IDAW) the CCW CDA pointer
does not contain the data address itself but a pointer to the IDAL.
This needs to be translated from physical to virtual as well before
using it.

This dereferencing is also used for dasd_page_cache and also fixed
although it is very unlikely that this code path ever gets used.

## References
- https://git.kernel.org/stable/c/b3a58f3b90f564f42a5c35778d8c5107b2c2150b
- https://git.kernel.org/stable/c/c116475f7d6410b1e6d399207ac75de6cf9c3652
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42099.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42099
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
