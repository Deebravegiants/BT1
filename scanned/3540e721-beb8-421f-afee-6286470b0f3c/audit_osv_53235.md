# [H] CVE-2022-3448

## Summary
Severity: High
Advisory: CVE-2022-3448
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-11-09
Source: https://osv.dev/vulnerability/CVE-2022-3448
Type: osv

## Details
Use after free in Permissions API in Google Chrome prior to 106.0.5249.119 allowed a remote attacker who convinced a user to engage in specific UI gestures to potentially exploit heap corruption via a crafted HTML page. (Chromium security severity: High)

## References
- https://security.gentoo.org/glsa/202305-10
- https://chromereleases.googleblog.com/2022/10/stable-channel-update-for-desktop_11.html
- https://crbug.com/1363040
