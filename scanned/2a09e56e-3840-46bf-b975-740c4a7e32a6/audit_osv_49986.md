# [H] CVE-2019-5797

## Summary
Severity: High
Advisory: CVE-2019-5797
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-09-29
Source: https://osv.dev/vulnerability/CVE-2019-5797
Type: osv

## Details
Double free in DOMStorage in Google Chrome prior to 73.0.3683.75 allowed a remote attacker to potentially exploit heap corruption via a crafted HTML page.

## References
- https://chromereleases.googleblog.com/2019/03/stable-channel-update-for-desktop_12.html
- https://crbug.com/916523
