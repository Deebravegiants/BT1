# [H] CVE-2017-15400

## Summary
Severity: High
Advisory: CVE-2017-15400
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-07
Source: https://osv.dev/vulnerability/CVE-2017-15400
Type: osv

## Details
Insufficient restriction of IPP filters in CUPS in Google Chrome OS prior to 62.0.3202.74 allowed a remote attacker to execute a command with the same privileges as the cups daemon via a crafted PPD file, aka a printer zeroconfig CRLF issue.

## References
- https://crbug.com/777215
- https://security.gentoo.org/glsa/201908-08
- https://www.debian.org/security/2018/dsa-4243
- https://chromereleases.googleblog.com/2017/10/stable-channel-update-for-chrome-os_27.html
