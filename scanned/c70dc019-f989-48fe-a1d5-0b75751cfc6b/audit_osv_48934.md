# [M] CVE-2018-18358

## Summary
Severity: Medium
Advisory: CVE-2018-18358
CVSS: 5.7 (CVSS:3.0/AV:A/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2018-12-11
Source: https://osv.dev/vulnerability/CVE-2018-18358
Type: osv

## Details
Lack of special casing of localhost in WPAD files in Google Chrome prior to 71.0.3578.80 allowed an attacker on the local network segment to proxy resources on localhost via a crafted WPAD file.

## References
- http://www.securityfocus.com/bid/106084
- https://crbug.com/899126
- https://access.redhat.com/errata/RHSA-2018:3803
- https://security.gentoo.org/glsa/201908-18
- https://www.debian.org/security/2018/dsa-4352
- https://chromereleases.googleblog.com/2018/12/stable-channel-update-for-desktop.html
