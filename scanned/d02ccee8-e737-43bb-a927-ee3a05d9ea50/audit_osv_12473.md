# [C] CVE-2018-12422

## Summary
Severity: Critical
Advisory: CVE-2018-12422
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-15
Source: https://osv.dev/vulnerability/CVE-2018-12422
Type: osv

## Details
addressbook/backends/ldap/e-book-backend-ldap.c in Evolution-Data-Server in GNOME Evolution through 3.29.2 might allow attackers to trigger a Buffer Overflow via a long query that is processed by the strcat function. NOTE: the software maintainer disputes this because "the code had computed the required string length first, and then allocated a large-enough buffer on the heap.

## References
- https://bugzilla.gnome.org/show_bug.cgi?id=796174
- https://gitlab.gnome.org/GNOME/evolution-data-server/commit/34bad6173
