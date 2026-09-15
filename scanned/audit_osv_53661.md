# [H] CVE-2023-1227

## Summary
Severity: High
Advisory: CVE-2023-1227
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-03-07
Source: https://osv.dev/vulnerability/CVE-2023-1227
Type: osv

## Details
Use after free in Core in Google Chrome on Lacros prior to 111.0.5563.64 allowed a remote attacker who convinced a user to engage in specific UI interaction to potentially exploit heap corruption via crafted UI interaction. (Chromium security severity: Medium)

## References
- https://chromereleases.googleblog.com/2023/03/stable-channel-update-for-desktop.html
- https://crbug.com/1348791
