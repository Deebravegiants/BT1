# [H] CVE-2022-1864

## Summary
Severity: High
Advisory: CVE-2022-1864
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-07-27
Source: https://osv.dev/vulnerability/CVE-2022-1864
Type: osv

## Details
Use after free in WebApp Installs in Google Chrome prior to 102.0.5005.61 allowed an attacker who convinced a user to install a malicious extension to potentially exploit heap corruption via a crafted Chrome Extension and specific user interaction.

## References
- https://chromereleases.googleblog.com/2022/05/stable-channel-update-for-desktop_24.html
- https://security.gentoo.org/glsa/202208-25
- https://crbug.com/1320624
