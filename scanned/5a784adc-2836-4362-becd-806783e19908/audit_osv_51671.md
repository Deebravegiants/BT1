# [H] CVE-2021-37974

## Summary
Severity: High
Advisory: CVE-2021-37974
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-10-08
Source: https://osv.dev/vulnerability/CVE-2021-37974
Type: osv

## Details
Use after free in Safebrowsing in Google Chrome prior to 94.0.4606.71 allowed a remote attacker who had compromised the renderer process to potentially exploit heap corruption via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FRFXUDH46PFVE75VQVWY6PYY5DK3S2XT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RNARCF5HEZK7GJXZRN5TQ45AQDCRM2WO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D63JZ3ROXCUHP4CFWDHCPZNTGET7T34R/
- https://www.debian.org/security/2022/dsa-5046
- https://chromereleases.googleblog.com/2021/09/stable-channel-update-for-desktop_30.html
- https://crbug.com/1245578
