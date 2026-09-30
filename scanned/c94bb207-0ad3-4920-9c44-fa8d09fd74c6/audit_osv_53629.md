# [H] CVE-2023-0932

## Summary
Severity: High
Advisory: CVE-2023-0932
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-02-22
Source: https://osv.dev/vulnerability/CVE-2023-0932
Type: osv

## Details
Use after free in WebRTC in Google Chrome on Windows prior to 110.0.5481.177 allowed a remote attacker who convinced the user to engage in specific UI interactions to potentially exploit heap corruption via a crafted HTML page. (Chromium security severity: High)

## References
- https://chromereleases.googleblog.com/2023/02/stable-channel-desktop-update_22.html
- https://security.gentoo.org/glsa/202309-17
- https://crbug.com/1413005
