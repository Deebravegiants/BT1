# [M] CVE-2019-5826

## Summary
Severity: Medium
Advisory: CVE-2019-5826
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-11-25
Source: https://osv.dev/vulnerability/CVE-2019-5826
Type: osv

## Details
Use after free in IndexedDB in Google Chrome prior to 73.0.3683.86 allowed a remote attacker who had compromised the renderer process to potentially exploit heap corruption via a crafted HTML page.

## References
- https://crbug.com/941746
- https://chromereleases.googleblog.com/2019/04/stable-channel-update-for-desktop_30.html
