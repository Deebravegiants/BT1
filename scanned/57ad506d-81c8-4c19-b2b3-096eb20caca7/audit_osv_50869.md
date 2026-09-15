# [C] CVE-2020-6461

## Summary
Severity: Critical
Advisory: CVE-2020-6461
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2020-05-21
Source: https://osv.dev/vulnerability/CVE-2020-6461
Type: osv

## Details
Use after free in storage in Google Chrome prior to 81.0.4044.129 allowed a remote attacker who had compromised the renderer process to potentially perform a sandbox escape via a crafted HTML page.

## References
- https://security.gentoo.org/glsa/202005-13
- https://www.debian.org/security/2020/dsa-4714
- https://chromereleases.googleblog.com/2020/04/stable-channel-update-for-desktop_27.html
- https://crbug.com/1072983
