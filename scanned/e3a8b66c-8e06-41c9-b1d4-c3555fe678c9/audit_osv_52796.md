# [C] CVE-2022-1312

## Summary
Severity: Critical
Advisory: CVE-2022-1312
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-07-25
Source: https://osv.dev/vulnerability/CVE-2022-1312
Type: osv

## Details
Use after free in storage in Google Chrome prior to 100.0.4896.88 allowed an attacker who convinced a user to install a malicious extension to potentially perform a sandbox escape via a crafted Chrome Extension.

## References
- https://chromereleases.googleblog.com/2022/04/stable-channel-update-for-desktop_11.html
- https://security.gentoo.org/glsa/202208-25
- https://crbug.com/1311701
