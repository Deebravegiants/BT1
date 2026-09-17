# [H] CVE-2022-2998

## Summary
Severity: High
Advisory: CVE-2022-2998
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-09-26
Source: https://osv.dev/vulnerability/CVE-2022-2998
Type: osv

## Details
Use after free in Browser Creation in Google Chrome prior to 104.0.5112.101 allowed a remote attacker who had convinced a user to engage in a specific UI interaction to potentially exploit heap corruption via a crafted HTML page.

## References
- https://chromereleases.googleblog.com/2022/08/stable-channel-update-for-desktop_16.html
- https://crbug.com/1329794
