# [M] CVE-2024-0811

## Summary
Severity: Medium
Advisory: CVE-2024-0811
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2024-01-24
Source: https://osv.dev/vulnerability/CVE-2024-0811
Type: osv

## Details
Inappropriate implementation in Extensions API in Google Chrome prior to 121.0.6167.85 allowed an attacker who convinced a user to install a malicious extension to leak cross-origin data via a crafted Chrome Extension. (Chromium security severity: Low)

## References
- http://packetstormsecurity.com/files/177172/Chrome-chrome.pageCapture.saveAsMHTML-Extension-API-Blocked-Origin-Bypass.html
- https://chromereleases.googleblog.com/2024/01/stable-channel-update-for-desktop_23.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MMI6GXFONZV6HE3BPZO3AP6GUVQLG4JQ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VXDSGAFQD4BDB4IB2O4ZUSHC3JCVQEKC/
- https://crbug.com/1494490
