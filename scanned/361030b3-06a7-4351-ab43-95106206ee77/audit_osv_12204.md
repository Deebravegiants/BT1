# [H] CVE-2018-10900

## Summary
Severity: High
Advisory: CVE-2018-10900
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-26
Source: https://osv.dev/vulnerability/CVE-2018-10900
Type: osv

## Details
Network Manager VPNC plugin (aka networkmanager-vpnc) before version 1.2.6 is vulnerable to a privilege escalation attack. A new line character can be used to inject a Password helper parameter into the configuration data passed to VPNC, allowing an attacker to execute arbitrary commands as root.

## References
- https://download.gnome.org/sources/NetworkManager-vpnc/1.2/NetworkManager-vpnc-1.2.6.news
- https://lists.debian.org/debian-lts-announce/2018/07/msg00048.html
- https://security.gentoo.org/glsa/201808-03
- https://www.debian.org/security/2018/dsa-4253
- https://bugzilla.novell.com/show_bug.cgi?id=1101147
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10900
- https://gitlab.gnome.org/GNOME/NetworkManager-vpnc/commit/07ac18a32b4
- https://pulsesecurity.co.nz/advisories/NM-VPNC-Privesc
- https://www.exploit-db.com/exploits/45313/
