# [M] CVE-2024-45819

## Summary
Severity: Medium
Advisory: CVE-2024-45819
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-12-19
Source: https://osv.dev/vulnerability/CVE-2024-45819
Type: osv

## Details
PVH guests have their ACPI tables constructed by the toolstack.  The
construction involves building the tables in local memory, which are
then copied into guest memory.  While actually used parts of the local
memory are filled in correctly, excess space that is being allocated is
left with its prior contents.

## References
- http://www.openwall.com/lists/oss-security/2024/11/12/10
- http://www.openwall.com/lists/oss-security/2024/11/12/7
- http://www.openwall.com/lists/oss-security/2024/11/12/1
- http://xenbits.xen.org/xsa/advisory-464.html
- https://xenbits.xenproject.org/xsa/advisory-464.html
