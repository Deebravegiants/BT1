# [H] CVE-2021-23192

## Summary
Severity: High
Advisory: CVE-2021-23192
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-03-02
Source: https://osv.dev/vulnerability/CVE-2021-23192
Type: osv

## Details
A flaw was found in the way samba implemented DCE/RPC. If a client to a Samba server sent a very large DCE/RPC request, and chose to fragment it, an attacker could replace later fragments with their own data, bypassing the signature requirements.

## References
- https://security.gentoo.org/glsa/202309-06
- https://ubuntu.com/security/CVE-2021-23192
- https://bugzilla.redhat.com/show_bug.cgi?id=2019666
- https://www.samba.org/samba/security/CVE-2021-23192.html
