# [M] CVE-2023-2860

## Summary
Severity: Medium
Advisory: CVE-2023-2860
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-07-24
Source: https://osv.dev/vulnerability/CVE-2023-2860
Type: osv

## Details
An out-of-bounds read vulnerability was found in the SR-IPv6 implementation in the Linux kernel. The flaw exists within the processing of seg6 attributes. The issue results from the improper validation of user-supplied data, which can result in a read past the end of an allocated buffer. This flaw allows a privileged local user to disclose sensitive information on affected installations of the Linux kernel.

## References
- https://www.zerodayinitiative.com/advisories/ZDI-CAN-18511
- https://access.redhat.com/security/cve/CVE-2023-2860
- https://bugzilla.redhat.com/show_bug.cgi?id=2218122
