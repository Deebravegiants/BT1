# [M] CVE-2023-34320

## Summary
Severity: Medium
Advisory: CVE-2023-34320
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-08
Source: https://osv.dev/vulnerability/CVE-2023-34320
Type: osv

## Details
Cortex-A77 cores (r0p0 and r1p0) are affected by erratum 1508412
where software, under certain circumstances, could deadlock a core
due to the execution of either a load to device or non-cacheable memory,
and either a store exclusive or register read of the Physical
Address Register (PAR_EL1) in close proximity.

## References
- http://xenbits.xen.org/xsa/advisory-436.html
- https://xenbits.xenproject.org/xsa/advisory-436.html
