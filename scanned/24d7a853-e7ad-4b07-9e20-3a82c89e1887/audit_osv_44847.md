# [M] Overly long URLs crash the Mattermost Desktop App

## Summary
Severity: Medium
Advisory: CVE-2026-8683
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-15
Source: https://osv.dev/vulnerability/CVE-2026-8683
Type: osv

## Details
Mattermost Desktop App versions <=6.1 5.5.13.0 fail to account for attempting to open extremely long URLs in the Mattermost Desktop App which allows a malicious server owner to crash the application via including a script to call window.open on a very large URL. Mattermost Advisory ID: MMSA-2026-00652

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8683.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-8683
