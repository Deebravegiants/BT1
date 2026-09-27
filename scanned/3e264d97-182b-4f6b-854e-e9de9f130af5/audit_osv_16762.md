# [M] CVE-2019-9633

## Summary
Severity: Medium
Advisory: CVE-2019-9633
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-03-08
Source: https://osv.dev/vulnerability/CVE-2019-9633
Type: osv

## Details
gio/gsocketclient.c in GNOME GLib 2.59.2 does not ensure that a parent GTask remains alive during the execution of a connection-attempting enumeration, which allows remote attackers to cause a denial of service (g_socket_client_connected_callback mishandling and application crash) via a crafted web site, as demonstrated by GNOME Web (aka Epiphany).

## References
- http://www.securityfocus.com/bid/107391
- https://gitlab.gnome.org/GNOME/glib/issues/1649
