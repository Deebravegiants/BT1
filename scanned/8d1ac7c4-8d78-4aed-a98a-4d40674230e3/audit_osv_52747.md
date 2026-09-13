# [C] CVE-2022-0977

## Summary
Severity: Critical
Advisory: CVE-2022-0977
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-07-21
Source: https://osv.dev/vulnerability/CVE-2022-0977
Type: osv

## Details
Use after free in Browser UI in Google Chrome on Chrome OS prior to 99.0.4844.74 allowed a remote attacker who convinced a user to engage in specific user interaction to potentially exploit heap corruption via a crafted HTML page.

## References
- https://chromereleases.googleblog.com/2022/03/stable-channel-update-for-desktop_15.html
- https://security.gentoo.org/glsa/202208-25
- https://crbug.com/1299225
