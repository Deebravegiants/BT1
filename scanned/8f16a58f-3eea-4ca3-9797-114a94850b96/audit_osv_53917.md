# [H] CVE-2023-32257

## Summary
Severity: High
Advisory: CVE-2023-32257
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-24
Source: https://osv.dev/vulnerability/CVE-2023-32257
Type: osv

## Details
A flaw was found in the Linux kernel's ksmbd, a high-performance in-kernel SMB server. The specific flaw exists within the processing of SMB2_SESSION_SETUP and SMB2_LOGOFF commands. The issue results from the lack of proper locking when performing operations on an object. An attacker can leverage this vulnerability to execute code in the context of the kernel.

## References
- https://access.redhat.com/security/cve/CVE-2023-32257
- https://security.netapp.com/advisory/ntap-20230915-0011/
- https://www.zerodayinitiative.com/advisories/ZDI-CAN-20596/
- https://bugzilla.redhat.com/show_bug.cgi?id=2219806
