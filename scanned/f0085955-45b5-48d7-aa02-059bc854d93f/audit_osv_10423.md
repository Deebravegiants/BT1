# [M] CVE-2017-15422

## Summary
Severity: Medium
Advisory: CVE-2017-15422
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-08-28
Source: https://osv.dev/vulnerability/CVE-2017-15422
Type: osv

## Details
Integer overflow in international date handling in International Components for Unicode (ICU) for C/C++ before 60.1, as used in V8 in Google Chrome prior to 63.0.3239.84 and other products, allowed a remote attacker to perform an out of bounds memory read via a crafted HTML page.

## References
- https://crbug.com/774382
- https://usn.ubuntu.com/3610-1/
- https://access.redhat.com/errata/RHSA-2017:3401
- https://security.gentoo.org/glsa/201801-03
- https://www.debian.org/security/2018/dsa-4150
- https://chromereleases.googleblog.com/2017/12/stable-channel-update-for-desktop.html
