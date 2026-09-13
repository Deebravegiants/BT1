# [M] Mattermost Desktop App fails to restrict the allow list of domains which NTLM credentials are passed

## Summary
Severity: Medium
Advisory: CVE-2026-6517
CVSS: 6.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-06-15
Source: https://osv.dev/vulnerability/CVE-2026-6517
Type: osv

## Details
Mattermost Desktop App versions <=6.1 5.5.13.0 fail to restrict the allow list of domains to which NTLM credentials were forwarded to in the Mattermost Desktop App which allows any user on a server without the image proxy enabled to intercept other users credentials via embedding an image that routes to an external web server. Mattermost Advisory ID: MMSA-2026-00651

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6517.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-6517
