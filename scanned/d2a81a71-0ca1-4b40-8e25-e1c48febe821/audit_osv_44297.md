# [M] Posting a malicious markdown image crashes the Mattermost Desktop App

## Summary
Severity: Medium
Advisory: CVE-2026-8075
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-8075
Type: osv

## Details
Mattermost Desktop App versions <=6.2 5.5.13 6.0.2.0 fail to properly null check when checking for headers in the Mattermost Desktop App which allows any user to crash another channel members Desktop App via posting a malicious link with an embedded image that misses one of those headers. Mattermost Advisory ID: MMSA-2026-00668

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8075.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-8075
