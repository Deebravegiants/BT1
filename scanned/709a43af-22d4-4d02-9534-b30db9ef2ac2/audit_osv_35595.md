# [M] Mattermost Server Denial of Service via Animated GIF Emoji Upload

## Summary
Severity: Medium
Advisory: CVE-2026-10819
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-10819
Type: osv

## Details
Mattermost versions 11.6.x <= 11.6.5, 10.11.x <= 10.11.20, 11.8.x <= 11.8.1, 11.7.x <= 11.7.4 fail to limit the number of frames and enforce the file size cap on animated GIF uploads, which allows an authenticated attacker to cause a denial of service via a crafted animated GIF uploaded as a custom emoji.. Mattermost Advisory ID: MMSA-2026-00695

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10819.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-10819
