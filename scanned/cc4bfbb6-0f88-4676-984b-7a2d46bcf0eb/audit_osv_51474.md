# [H] CVE-2021-30602

## Summary
Severity: High
Advisory: CVE-2021-30602
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-26
Source: https://osv.dev/vulnerability/CVE-2021-30602
Type: osv

## Details
Use after free in WebRTC in Google Chrome prior to 92.0.4515.159 allowed an attacker who convinced a user to visit a malicious website to potentially exploit heap corruption via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5LVY4WIWTVVYKQMROJJS365TZBKEARCF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IPJPUSAWIJMQFBQQQYXAICLI4EKFQOH6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QW4R2K5HVJ4R6XDZYOJCCFPIN2XHNS3L/
- https://chromereleases.googleblog.com/2021/08/stable-channel-update-for-desktop.html
- https://crbug.com/1230767
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2021-1348
