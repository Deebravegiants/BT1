# [H] CVE-2022-3654

## Summary
Severity: High
Advisory: CVE-2022-3654
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/CVE-2022-3654
Type: osv

## Details
Use after free in Layout in Google Chrome prior to 107.0.5304.62 allowed a remote attacker to potentially exploit heap corruption via a crafted HTML page. (Chromium security severity: High)

## References
- https://chromereleases.googleblog.com/2022/10/stable-channel-update-for-desktop_25.html
- http://packetstormsecurity.com/files/170012/Chrome-blink-LocalFrameView-PerformLayout-Use-After-Free.html
- https://crbug.com/1365330
