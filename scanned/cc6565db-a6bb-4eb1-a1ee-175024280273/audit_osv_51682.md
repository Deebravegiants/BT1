# [H] CVE-2021-37985

## Summary
Severity: High
Advisory: CVE-2021-37985
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-11-02
Source: https://osv.dev/vulnerability/CVE-2021-37985
Type: osv

## Details
Use after free in V8 in Google Chrome prior to 95.0.4638.54 allowed a remote attacker who had convinced a user to allow for connection to debugger to potentially exploit heap corruption via a crafted HTML page.

## References
- https://chromereleases.googleblog.com/2021/10/stable-channel-update-for-desktop_19.html
- https://www.debian.org/security/2022/dsa-5046
- https://crbug.com/1241860
