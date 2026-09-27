# [H] CVE-2016-10156

## Summary
Severity: High
Advisory: CVE-2016-10156
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2016-10156
Type: osv

## Details
A flaw in systemd v228 in /src/basic/fs-util.c caused world writable suid files to be created when using the systemd timers features, allowing local attackers to escalate their privileges to root. This is fixed in v229.

## References
- http://www.securitytracker.com/id/1037686
- https://www.exploit-db.com/exploits/41171/
- http://www.securityfocus.com/bid/95790
- https://bugzilla.suse.com/show_bug.cgi?id=1020601
- https://github.com/systemd/systemd/commit/06eeacb6fe029804f296b065b3ce91e796e1cd0e
- https://github.com/systemd/systemd/commit/ee735086f8670be1591fa9593e80dd60163a7a2f
