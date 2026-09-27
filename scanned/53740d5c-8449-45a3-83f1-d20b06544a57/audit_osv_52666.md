# [C] CVE-2022-0290

## Summary
Severity: Critical
Advisory: CVE-2022-0290
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-02-12
Source: https://osv.dev/vulnerability/CVE-2022-0290
Type: osv

## Details
Use after free in Site isolation in Google Chrome prior to 97.0.4692.99 allowed a remote attacker to potentially perform a sandbox escape via a crafted HTML page.

## References
- http://packetstormsecurity.com/files/166080/Chrome-RenderFrameHostImpl-Use-After-Free.html
- https://chromereleases.googleblog.com/2022/01/stable-channel-update-for-desktop_19.html
- https://crbug.com/1260134
