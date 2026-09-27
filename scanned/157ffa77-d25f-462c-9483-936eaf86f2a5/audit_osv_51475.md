# [H] CVE-2021-30603

## Summary
Severity: High
Advisory: CVE-2021-30603
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-26
Source: https://osv.dev/vulnerability/CVE-2021-30603
Type: osv

## Details
Data race in WebAudio in Google Chrome prior to 92.0.4515.159 allowed a remote attacker to potentially exploit heap corruption via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IPJPUSAWIJMQFBQQQYXAICLI4EKFQOH6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QW4R2K5HVJ4R6XDZYOJCCFPIN2XHNS3L/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5LVY4WIWTVVYKQMROJJS365TZBKEARCF/
- http://packetstormsecurity.com/files/164259/Chrome-HRTFDatabaseLoader-WaitForLoaderThreadCompletion-Data-Race.html
- https://chromereleases.googleblog.com/2021/08/stable-channel-update-for-desktop.html
- https://crbug.com/1233564
