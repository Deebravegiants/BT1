# [H] CVE-2016-5199

## Summary
Severity: High
Advisory: CVE-2016-5199
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-01-19
Source: https://osv.dev/vulnerability/CVE-2016-5199
Type: osv

## Details
An off by one error resulting in an allocation of zero size in FFmpeg in Google Chrome prior to 54.0.2840.98 for Mac, and 54.0.2840.99 for Windows, and 54.0.2840.100 for Linux, and 55.0.2883.84 for Android allowed a remote attacker to potentially exploit heap corruption via a crafted video file.

## References
- http://www.securityfocus.com/bid/94196
- http://www.securitytracker.com/id/1037273
- https://crbug.com/643948
- https://security.gentoo.org/glsa/201611-16
- http://rhn.redhat.com/errata/RHSA-2016-2718.html
- https://chromereleases.googleblog.com/2016/11/stable-channel-update-for-desktop_9.html
