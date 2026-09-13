# [H] CVE-2022-3039

## Summary
Severity: High
Advisory: CVE-2022-3039
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-09-26
Source: https://osv.dev/vulnerability/CVE-2022-3039
Type: osv

## Details
Use after free in WebSQL in Google Chrome prior to 105.0.5195.52 allowed a remote attacker to potentially exploit heap corruption via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T4NMJURTG5RO3TGD7ZMIQ6Z4ZZ3SAVYE/
- https://chromereleases.googleblog.com/2022/08/stable-channel-update-for-desktop_30.html
- https://security.gentoo.org/glsa/202209-23
- https://crbug.com/1343348
