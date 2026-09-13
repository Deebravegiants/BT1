# [H] CVE-2021-37998

## Summary
Severity: High
Advisory: CVE-2021-37998
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-11-23
Source: https://osv.dev/vulnerability/CVE-2021-37998
Type: osv

## Details
Use after free in Garbage Collection in Google Chrome prior to 95.0.4638.69 allowed a remote attacker to potentially exploit heap corruption via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3W46HRT2UVHWSLZB6JZHQF6JNQWKV744/
- https://chromereleases.googleblog.com/2021/10/stable-channel-update-for-desktop_28.html
- https://www.debian.org/security/2022/dsa-5046
- https://crbug.com/1259587
