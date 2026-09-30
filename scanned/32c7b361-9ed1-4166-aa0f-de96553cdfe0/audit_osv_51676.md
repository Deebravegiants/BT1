# [H] CVE-2021-37979

## Summary
Severity: High
Advisory: CVE-2021-37979
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-11-02
Source: https://osv.dev/vulnerability/CVE-2021-37979
Type: osv

## Details
heap buffer overflow in WebRTC in Google Chrome prior to 94.0.4606.81 allowed a remote attacker who convinced a user to browse to a malicious website to potentially exploit heap corruption via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RNARCF5HEZK7GJXZRN5TQ45AQDCRM2WO/
- https://www.debian.org/security/2022/dsa-5046
- https://chromereleases.googleblog.com/2021/10/stable-channel-update-for-desktop.html
- https://crbug.com/1247260
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2021-1372
