# [C] CVE-2017-7875

## Summary
Severity: Critical
Advisory: CVE-2017-7875
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2017-7875
Type: osv

## Details
In wallpaper.c in feh before v2.18.3, if a malicious client pretends to be the E17 window manager, it is possible to trigger an out-of-boundary heap write while receiving an IPC message. An integer overflow leads to a buffer overflow and/or a double free.

## References
- https://lists.debian.org/debian-lts-announce/2020/05/msg00021.html
- http://www.securityfocus.com/bid/97689
- https://security.gentoo.org/glsa/201707-08
- https://feh.finalrewind.org/
- https://github.com/derf/feh/commit/f7a547b7ef8fc8ebdeaa4c28515c9d72e592fb6d
