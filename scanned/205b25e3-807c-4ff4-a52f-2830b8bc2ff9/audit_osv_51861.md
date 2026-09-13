# [H] CVE-2021-4320

## Summary
Severity: High
Advisory: CVE-2021-4320
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-07-29
Source: https://osv.dev/vulnerability/CVE-2021-4320
Type: osv

## Details
Use after free in Blink in Google Chrome prior to 92.0.4515.107 allowed a remote attacker who had compromised the renderer process to perform arbitrary read/write via a crafted HTML page. (Chromium security severity: High)

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PQKT7EGDD2P3L7S3NXEDDRCPK4NNZNWJ/
- https://chromereleases.googleblog.com/2021/07/stable-channel-update-for-desktop_20.html
- https://crbug.com/1224238
