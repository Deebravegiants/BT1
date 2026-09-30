# [C] CVE-2021-21107

## Summary
Severity: Critical
Advisory: CVE-2021-21107
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2021-01-08
Source: https://osv.dev/vulnerability/CVE-2021-21107
Type: osv

## Details
Use after free in drag and drop in Google Chrome on Linux prior to 87.0.4280.141 allowed a remote attacker who had compromised the renderer process to potentially perform a sandbox escape via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VVUWIJKZTZTG6G475OR6PP4WPQBVM6PS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Z6P6AVVFP7B2M4H7TJQBASRZIBLOTUFN/
- https://security.gentoo.org/glsa/202101-05
- https://www.debian.org/security/2021/dsa-4832
- https://chromereleases.googleblog.com/2021/01/stable-channel-update-for-desktop.html
- https://crbug.com/1153595
