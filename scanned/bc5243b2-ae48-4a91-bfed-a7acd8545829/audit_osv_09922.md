# [M] CVE-2017-12164

## Summary
Severity: Medium
Advisory: CVE-2017-12164
CVSS: 6.4 (CVSS:3.0/AV:P/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-26
Source: https://osv.dev/vulnerability/CVE-2017-12164
Type: osv

## Details
A flaw was discovered in gdm 3.24.1 where gdm greeter was no longer setting the ran_once boolean during autologin. If autologin was enabled for a victim, an attacker could simply select 'login as another user' to unlock their screen.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-12164
- https://gitlab.gnome.org/GNOME/gdm/commit/ff98b28
