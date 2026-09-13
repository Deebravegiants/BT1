# [H] CVE-2023-39179

## Summary
Severity: High
Advisory: CVE-2023-39179
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-11-18
Source: https://osv.dev/vulnerability/CVE-2023-39179
Type: osv

## Details
A flaw was found within the handling of SMB2 read requests in the kernel ksmbd module. The issue results from the lack of proper validation of user-supplied data, which can result in a read past the end of an allocated buffer. An attacker can leverage this to disclose sensitive information on affected installations of Linux. Only systems with ksmbd enabled are vulnerable to this CVE.

## References
- https://access.redhat.com/security/cve/CVE-2023-39179
- https://bugzilla.redhat.com/show_bug.cgi?id=2326529
- https://www.zerodayinitiative.com/advisories/ZDI-24-586/
- https://bugzilla.redhat.com/show_bug.cgi?id=2326529
