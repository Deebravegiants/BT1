# [M] CVE-2018-20067

## Summary
Severity: Medium
Advisory: CVE-2018-20067
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2019-01-09
Source: https://osv.dev/vulnerability/CVE-2018-20067
Type: osv

## Details
A renderer initiated back navigation was incorrectly allowed to cancel a browser initiated one in Navigation in Google Chrome prior to 71.0.3578.80 allowed a remote attacker to confuse the user about the origin of the current page via a crafted HTML page.

## References
- https://crbug.com/879965
- https://chromereleases.googleblog.com/2018/12/stable-channel-update-for-desktop.html
