# [H] CVE-2022-0793

## Summary
Severity: High
Advisory: CVE-2022-0793
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-04-05
Source: https://osv.dev/vulnerability/CVE-2022-0793
Type: osv

## Details
Use after free in Cast in Google Chrome prior to 99.0.4844.51 allowed an attacker who convinced a user to install a malicious extension and engage in specific user interaction to potentially exploit heap corruption via a crafted Chrome Extension.

## References
- https://chromereleases.googleblog.com/2022/03/stable-channel-update-for-desktop.html
- https://security.gentoo.org/glsa/202208-25
- https://crbug.com/1291728
