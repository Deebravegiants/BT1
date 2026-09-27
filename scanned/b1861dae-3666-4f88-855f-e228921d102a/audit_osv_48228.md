# [M] CVE-2017-5025

## Summary
Severity: Medium
Advisory: CVE-2017-5025
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-17
Source: https://osv.dev/vulnerability/CVE-2017-5025
Type: osv

## Details
FFmpeg in Google Chrome prior to 56.0.2924.76 for Linux, Windows and Mac, failed to perform proper bounds checking, which allowed a remote attacker to potentially exploit heap corruption via a crafted video file.

## References
- http://www.securityfocus.com/bid/95792
- http://www.securitytracker.com/id/1037718
- https://crbug.com/643950
- http://rhn.redhat.com/errata/RHSA-2017-0206.html
- http://www.debian.org/security/2017/dsa-3776
- https://security.gentoo.org/glsa/201701-66
- https://security.gentoo.org/glsa/201705-05
- https://chromereleases.googleblog.com/2017/01/stable-channel-update-for-desktop.html
