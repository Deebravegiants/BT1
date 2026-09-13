# [M] CVE-2017-15396

## Summary
Severity: Medium
Advisory: CVE-2017-15396
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-08-28
Source: https://osv.dev/vulnerability/CVE-2017-15396
Type: osv

## Details
A stack buffer overflow in NumberingSystem in International Components for Unicode (ICU) for C/C++ before 60.2, as used in V8 in Google Chrome prior to 62.0.3202.75 and other products, allowed a remote attacker to potentially exploit heap corruption via a crafted HTML page.

## References
- http://bugs.icu-project.org/trac/changeset/40494
- http://www.securityfocus.com/bid/101597
- https://crbug.com/770452
- https://access.redhat.com/errata/RHSA-2017:3082
- https://security.gentoo.org/glsa/201711-02
- https://www.debian.org/security/2017/dsa-4020
- https://chromereleases.googleblog.com/2017/10/stable-channel-update-for-desktop_26.html
