# [H] CVE-2016-10369

## Summary
Severity: High
Advisory: CVE-2016-10369
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-08
Source: https://osv.dev/vulnerability/CVE-2016-10369
Type: osv

## Details
unixsocket.c in lxterminal through 0.3.0 insecurely uses /tmp for a socket file, allowing a local user to cause a denial of service (preventing terminal launch), or possibly have other impact (bypassing terminal access control).

## References
- https://git.lxde.org/gitweb/?p=lxde/lxterminal.git%3Ba=commit%3Bh=f99163c6ff8b2f57c5f37b1ce5d62cf7450d4648
- https://unix.stackexchange.com/questions/333539/lxterminal-in-the-netstat-output/333578
- https://bugs.debian.org/862098
