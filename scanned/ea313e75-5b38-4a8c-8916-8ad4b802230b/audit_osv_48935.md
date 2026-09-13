# [H] CVE-2018-18359

## Summary
Severity: High
Advisory: CVE-2018-18359
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-11
Source: https://osv.dev/vulnerability/CVE-2018-18359
Type: osv

## Details
Incorrect handling of Reflect.construct in V8 in Google Chrome prior to 71.0.3578.80 allowed a remote attacker to perform an out of bounds memory read via a crafted HTML page.

## References
- https://crbug.com/907714
- http://www.securityfocus.com/bid/106084
- https://access.redhat.com/errata/RHSA-2018:3803
- https://security.gentoo.org/glsa/201908-18
- https://www.debian.org/security/2018/dsa-4352
- https://chromereleases.googleblog.com/2018/12/stable-channel-update-for-desktop.html
