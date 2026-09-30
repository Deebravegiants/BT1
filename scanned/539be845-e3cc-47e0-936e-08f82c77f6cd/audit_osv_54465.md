# [H] CVE-2023-6706

## Summary
Severity: High
Advisory: CVE-2023-6706
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-12-14
Source: https://osv.dev/vulnerability/CVE-2023-6706
Type: osv

## Details
Use after free in FedCM in Google Chrome prior to 120.0.6099.109 allowed a remote attacker who convinced a user to engage in specific UI interaction to potentially exploit heap corruption via a crafted HTML page. (Chromium security severity: High)

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6NWZ23ZJ62XKWVNGHSIZQYILVJWH5BLI/
- https://chromereleases.googleblog.com/2023/12/stable-channel-update-for-desktop_12.html
- https://security.gentoo.org/glsa/202401-34
- https://crbug.com/1500921
