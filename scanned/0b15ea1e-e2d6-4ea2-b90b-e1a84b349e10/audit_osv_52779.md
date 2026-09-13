# [H] CVE-2022-1145

## Summary
Severity: High
Advisory: CVE-2022-1145
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-07-23
Source: https://osv.dev/vulnerability/CVE-2022-1145
Type: osv

## Details
Use after free in Extensions in Google Chrome prior to 100.0.4896.60 allowed an attacker who convinced a user to install a malicious extension to potentially exploit heap corruption via specific user interaction and profile destruction.

## References
- https://chromereleases.googleblog.com/2022/03/stable-channel-update-for-desktop_29.html
- https://security.gentoo.org/glsa/202208-25
- https://crbug.com/1304545
