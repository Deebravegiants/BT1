# [H] CVE-2023-32252

## Summary
Severity: High
Advisory: CVE-2023-32252
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-24
Source: https://osv.dev/vulnerability/CVE-2023-32252
Type: osv

## Details
A flaw was found in the Linux kernel's ksmbd, a high-performance in-kernel SMB server. The specific flaw exists within the handling of SMB2_LOGOFF commands. The issue results from the lack of proper validation of a pointer prior to accessing it. An attacker can leverage this vulnerability to create a denial-of-service condition on the system.

## References
- https://access.redhat.com/security/cve/CVE-2023-32252
- https://security.netapp.com/advisory/ntap-20231124-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=2219815
- https://www.zerodayinitiative.com/advisories/ZDI-CAN-20590/
