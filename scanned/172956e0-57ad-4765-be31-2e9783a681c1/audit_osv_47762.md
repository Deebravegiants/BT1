# [H] CVE-2017-11565

## Summary
Severity: High
Advisory: CVE-2017-11565
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-07-23
Source: https://osv.dev/vulnerability/CVE-2017-11565
Type: osv

## Details
debian/tor.init in the Debian tor_0.2.9.11-1~deb9u1 package for Tor was designed to execute aa-exec from the standard system pathname if the apparmor package is installed, but implements this incorrectly (with a wrong assumption that the specific pathname would remain the same forever), which allows attackers to bypass intended AppArmor restrictions by leveraging the silent loss of this protection mechanism. NOTE: this does not affect systems, such as default Debian stretch installations, on which Tor startup relies on a systemd unit file (instead of this tor.init script).

## References
- http://www.securityfocus.com/bid/99933
- https://bugs.debian.org/869153
