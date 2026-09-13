# [H] CVE-2021-30575

## Summary
Severity: High
Advisory: CVE-2021-30575
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-03
Source: https://osv.dev/vulnerability/CVE-2021-30575
Type: osv

## Details
Out of bounds write in Autofill in Google Chrome prior to 92.0.4515.107 allowed a remote attacker who had compromised the renderer process to potentially exploit heap corruption via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5LVY4WIWTVVYKQMROJJS365TZBKEARCF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IPJPUSAWIJMQFBQQQYXAICLI4EKFQOH6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QW4R2K5HVJ4R6XDZYOJCCFPIN2XHNS3L/
- https://chromereleases.googleblog.com/2021/07/stable-channel-update-for-desktop_20.html
- https://crbug.com/1213313
