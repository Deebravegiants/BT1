# [C] CVE-2020-6493

## Summary
Severity: Critical
Advisory: CVE-2020-6493
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2020-06-03
Source: https://osv.dev/vulnerability/CVE-2020-6493
Type: osv

## Details
Use after free in WebAuthentication in Google Chrome prior to 83.0.4103.97 allowed a remote attacker who had compromised the renderer process to potentially perform a sandbox escape via a crafted HTML page.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00034.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00038.html
- https://chromereleases.googleblog.com/2020/06/stable-channel-update-for-desktop.html
- https://security.gentoo.org/glsa/202006-02
- https://www.debian.org/security/2020/dsa-4714
- https://crbug.com/1082105
