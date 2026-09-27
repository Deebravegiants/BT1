# [C] CVE-2022-2010

## Summary
Severity: Critical
Advisory: CVE-2022-2010
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:H)
Published: 2022-07-28
Source: https://osv.dev/vulnerability/CVE-2022-2010
Type: osv

## Details
Out of bounds read in compositing in Google Chrome prior to 102.0.5005.115 allowed a remote attacker who had compromised the renderer process to potentially perform a sandbox escape via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T4NMJURTG5RO3TGD7ZMIQ6Z4ZZ3SAVYE/
- https://security.gentoo.org/glsa/202208-25
- https://chromereleases.googleblog.com/2022/06/stable-channel-update-for-desktop.html
- https://crbug.com/1325298
