# [H] CVE-2020-25721

## Summary
Severity: High
Advisory: CVE-2020-25721
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-16
Source: https://osv.dev/vulnerability/CVE-2020-25721
Type: osv

## Details
Kerberos acceptors need easy access to stable AD identifiers (eg objectSid). Samba as an AD DC now provides a way for Linux applications to obtain a reliable SID (and samAccountName) in issued tickets.

## References
- https://security.gentoo.org/glsa/202309-06
- https://www.samba.org/samba/security/CVE-2020-25721.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2021728
- https://bugzilla.samba.org/show_bug.cgi?id=14725
