# [M] Opening a window with {{javascript:alert()}} as URL causes crash in the Mattermost Desktop App

## Summary
Severity: Medium
Advisory: CVE-2026-3471
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-18
Source: https://osv.dev/vulnerability/CVE-2026-3471
Type: osv

## Details
Mattermost Desktop App versions <=6.1 6.0.1 5.4.13.0 fail to prevent an invalid URL from loading in a pop-up window in the Mattermost Desktop App which allows a malicious server owner to repeated crash the application via calling {{window.open('javascript:alert()');}}. Mattermost Advisory ID: MMSA-2026-00618

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3471.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-3471
