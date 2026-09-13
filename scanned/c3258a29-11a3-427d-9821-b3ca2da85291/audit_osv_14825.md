# [C] CVE-2019-11772

## Summary
Severity: Critical
Advisory: CVE-2019-11772
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-17
Source: https://osv.dev/vulnerability/CVE-2019-11772
Type: osv

## Details
In Eclipse OpenJ9 prior to 0.15, the String.getBytes(int, int, byte[], int) method does not verify that the provided byte array is non-null nor that the provided index is in bounds when compiled by the JIT. This allows arbitrary writes to any 32-bit address or beyond the end of a byte array within Java code run under a SecurityManager.

## References
- https://access.redhat.com/errata/RHSA-2019:2585
- https://access.redhat.com/errata/RHSA-2019:2590
- https://access.redhat.com/errata/RHSA-2019:2592
- https://access.redhat.com/errata/RHSA-2019:2737
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=549075
