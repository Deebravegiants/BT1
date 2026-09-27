# [C] CVE-2017-12186

## Summary
Severity: Critical
Advisory: CVE-2017-12186
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-24
Source: https://osv.dev/vulnerability/CVE-2017-12186
Type: osv

## Details
xorg-x11-server before 1.19.5 was missing length validation in X-Resource extension allowing malicious X client to cause X server to crash or possibly execute arbitrary code.

## References
- https://www.debian.org/security/2017/dsa-4000
- https://bugzilla.redhat.com/show_bug.cgi?id=1509216
- https://cgit.freedesktop.org/xorg/xserver/commit/?id=cad5a1050b7184d828aef9c1dd151c3ab649d37e
