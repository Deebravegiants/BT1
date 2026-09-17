# [H] ALPINE-CVE-2019-12795

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-12795
Ecosystem: Alpine:v3.7, Alpine:v3.8
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12795
Type: osv

## Affected
- Alpine:v3.7: `gvfs` — affected >=1.40.0 <1.34.1-r1
- Alpine:v3.8: `gvfs` — affected >=1.40.0 <1.36.1-r1

## Details
daemon/gvfsdaemon.c in gvfsd from GNOME gvfs before 1.38.3, 1.40.x before 1.40.2, and 1.41.x before 1.41.3 opened a private D-Bus server socket without configuring an authorization rule. A local attacker could connect to this server socket and issue D-Bus method calls. (Note that the server socket only accepts a single connection, so the attacker would have to discover the server and connect to the socket before its owner does.)

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12795
