# [H] CVE-2021-40905

## Summary
Severity: High
Advisory: CVE-2021-40905
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-03-25
Source: https://osv.dev/vulnerability/CVE-2021-40905
Type: osv

## Details
The web management console of CheckMK Enterprise Edition (versions 1.5.0 to 2.0.0p9) does not properly sanitise the uploading of ".mkp" files, which are Extension Packages, making remote code execution possible. Successful exploitation requires access to the web management interface, either with valid credentials or with a hijacked session of a user with administrator role. NOTE: the vendor states that this is the intended behavior: admins are supposed to be able to execute code in this manner.

## References
- https://docs.checkmk.com/latest/en/mkps.html
- https://github.com/Edgarloyola/CVE-2021-40905
