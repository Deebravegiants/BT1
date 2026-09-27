# [C] CVE-2016-10727

## Summary
Severity: Critical
Advisory: CVE-2016-10727
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-20
Source: https://osv.dev/vulnerability/CVE-2016-10727
Type: osv

## Details
camel/providers/imapx/camel-imapx-server.c in the IMAPx component in GNOME evolution-data-server before 3.21.2 proceeds with cleartext data containing a password if the client wishes to use STARTTLS but the server will not use STARTTLS, which makes it easier for remote attackers to obtain sensitive information by sniffing the network. The server code was intended to report an error and not proceed, but the code was written incorrectly.

## References
- https://github.com/GNOME/evolution-data-server/releases/tag/EVOLUTION_DATA_SERVER_3_21_2
- https://gitlab.gnome.org/GNOME/evolution-data-server/blob/master/NEWS#L1022
- https://usn.ubuntu.com/3724-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=1334842
- https://gitlab.gnome.org/GNOME/evolution-data-server/commit/f26a6f67
