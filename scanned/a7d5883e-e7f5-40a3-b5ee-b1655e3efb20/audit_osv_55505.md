# [M] CVE-2025-60018

## Summary
Severity: Medium
Advisory: CVE-2025-60018
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2025-09-25
Source: https://osv.dev/vulnerability/CVE-2025-60018
Type: osv

## Details
glib-networking's OpenSSL backend fails to properly check the return value of a call to BIO_write(), resulting in an out of bounds read.

## References
- https://access.redhat.com/security/cve/CVE-2025-60018
- https://bugzilla.redhat.com/show_bug.cgi?id=2398135
- https://gitlab.gnome.org/GNOME/glib-networking/-/issues/226
