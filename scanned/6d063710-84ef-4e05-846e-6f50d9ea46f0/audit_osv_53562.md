# [C] CVE-2022-4924

## Summary
Severity: Critical
Advisory: CVE-2022-4924
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2023-07-29
Source: https://osv.dev/vulnerability/CVE-2022-4924
Type: osv

## Details
Use after free in WebRTC in Google Chrome prior to 97.0.4692.71 allowed a remote attacker who had compromised the renderer process to potentially perform a sandbox escape via a crafted HTML page. (Chromium security severity: High)

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PQKT7EGDD2P3L7S3NXEDDRCPK4NNZNWJ/
- https://chromereleases.googleblog.com/2022/01/stable-channel-update-for-desktop.html
- https://crbug.com/1272967
