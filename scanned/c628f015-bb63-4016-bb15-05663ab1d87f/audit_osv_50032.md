# [C] CVE-2019-5850

## Summary
Severity: Critical
Advisory: CVE-2019-5850
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2019-11-25
Source: https://osv.dev/vulnerability/CVE-2019-5850
Type: osv

## Details
Use after free in offline mode in Google Chrome prior to 76.0.3809.87 allowed a remote attacker who had compromised the renderer process to potentially perform a sandbox escape via a crafted HTML page.

## References
- https://crbug.com/977462
- https://chromereleases.googleblog.com/2019/07/stable-channel-update-for-desktop_30.html
