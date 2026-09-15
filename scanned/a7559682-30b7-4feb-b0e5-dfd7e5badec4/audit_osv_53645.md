# [H] CVE-2023-1194

## Summary
Severity: High
Advisory: CVE-2023-1194
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-11-03
Source: https://osv.dev/vulnerability/CVE-2023-1194
Type: osv

## Details
An out-of-bounds (OOB) memory read flaw was found in parse_lease_state in the KSMBD implementation of the in-kernel samba server and CIFS in the Linux kernel. When an attacker sends the CREATE command with a malformed payload to KSMBD, due to a missing check of `NameOffset` in the `parse_lease_state()` function, the `create_context` object can access invalid memory.

## References
- https://security.netapp.com/advisory/ntap-20231221-0006/
- https://access.redhat.com/security/cve/CVE-2023-1194
- https://bugzilla.redhat.com/show_bug.cgi?id=2154176
- https://www.spinics.net/lists/stable-commits/msg303065.html
