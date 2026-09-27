# [H] CVE-2023-39180

## Summary
Severity: High
Advisory: CVE-2023-39180
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-18
Source: https://osv.dev/vulnerability/CVE-2023-39180
Type: osv

## Details
A flaw was found within the handling of SMB2_READ commands in the kernel ksmbd module. The issue results from not releasing memory after its effective lifetime. An attacker can leverage this to create a denial-of-service condition on affected installations of Linux. Authentication is not required to exploit this vulnerability, but only systems with ksmbd enabled are vulnerable.

## References
- https://access.redhat.com/security/cve/CVE-2023-39180
- https://bugzilla.redhat.com/show_bug.cgi?id=2326531
- https://www.zerodayinitiative.com/advisories/ZDI-24-589/
- https://bugzilla.redhat.com/show_bug.cgi?id=2326531
