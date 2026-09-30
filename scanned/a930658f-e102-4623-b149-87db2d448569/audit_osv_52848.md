# [C] CVE-2022-1853

## Summary
Severity: Critical
Advisory: CVE-2022-1853
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-07-27
Source: https://osv.dev/vulnerability/CVE-2022-1853
Type: osv

## Details
Use after free in Indexed DB in Google Chrome prior to 102.0.5005.61 allowed a remote attacker to potentially perform a sandbox escape via a crafted HTML page.

## References
- https://chromereleases.googleblog.com/2022/05/stable-channel-update-for-desktop_24.html
- https://security.gentoo.org/glsa/202208-25
- https://crbug.com/1324864
