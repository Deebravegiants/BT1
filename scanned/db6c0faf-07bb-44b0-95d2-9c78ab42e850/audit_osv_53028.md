# [H] CVE-2022-2624

## Summary
Severity: High
Advisory: CVE-2022-2624
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-08-12
Source: https://osv.dev/vulnerability/CVE-2022-2624
Type: osv

## Details
Heap buffer overflow in PDF in Google Chrome prior to 104.0.5112.79 allowed a remote attacker who convinced a user to engage in specific user interactions to potentially exploit heap corruption via a crafted PDF file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T4NMJURTG5RO3TGD7ZMIQ6Z4ZZ3SAVYE/
- https://security.gentoo.org/glsa/202208-35
- https://chromereleases.googleblog.com/2022/08/stable-channel-update-for-desktop.html
- https://crbug.com/1339745
