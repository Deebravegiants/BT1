# [H] CVE-2025-58149

## Summary
Severity: High
Advisory: CVE-2025-58149
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-10-31
Source: https://osv.dev/vulnerability/CVE-2025-58149
Type: osv

## Details
When passing through PCI devices, the detach logic in libxl won't remove
access permissions to any 64bit memory BARs the device might have.  As a
result a domain can still have access any 64bit memory BAR when such
device is no longer assigned to the domain.

For PV domains the permission leak allows the domain itself to map the memory
in the page-tables.  For HVM it would require a compromised device model or
stubdomain to map the leaked memory into the HVM domain p2m.

## References
- https://xenbits.xenproject.org/xsa/advisory-476.html
- http://www.openwall.com/lists/oss-security/2025/10/24/1
- http://xenbits.xen.org/xsa/advisory-476.html
