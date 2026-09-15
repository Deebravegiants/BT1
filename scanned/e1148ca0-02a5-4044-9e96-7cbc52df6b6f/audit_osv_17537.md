# [H] CVE-2020-16118

## Summary
Severity: High
Advisory: CVE-2020-16118
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-07-29
Source: https://osv.dev/vulnerability/CVE-2020-16118
Type: osv

## Details
In GNOME Balsa before 2.6.0, a malicious server operator or man in the middle can trigger a NULL pointer dereference and client crash by sending a PREAUTH response to imap_mbox_connect in libbalsa/imap/imap-handle.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00035.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00045.html
- https://gitlab.gnome.org/GNOME/balsa/-/commit/4e245d758e1c826a01080d40c22ca8706f0339e5
- https://gitlab.gnome.org/GNOME/balsa/-/issues/23
