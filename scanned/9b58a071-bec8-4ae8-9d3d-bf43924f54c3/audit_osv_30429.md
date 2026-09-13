# [C] CVE-2024-52533

## Summary
Severity: Critical
Advisory: CVE-2024-52533
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-11
Source: https://osv.dev/vulnerability/CVE-2024-52533
Type: osv

## Details
gio/gsocks4aproxy.c in GNOME GLib before 2.82.1 has an off-by-one error and resultant buffer overflow because SOCKS4_CONN_MSG_LEN is not sufficient for a trailing '\0' character.

## References
- http://www.openwall.com/lists/oss-security/2024/11/12/11
- https://gitlab.gnome.org/GNOME/glib/-/releases/2.82.1
- https://gitlab.gnome.org/Teams/Releng/security/-/wikis/home
- https://lists.debian.org/debian-lts-announce/2024/11/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52533.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-52533
- https://security.netapp.com/advisory/ntap-20241206-0009/
- https://gitlab.gnome.org/GNOME/glib/-/issues/3461
