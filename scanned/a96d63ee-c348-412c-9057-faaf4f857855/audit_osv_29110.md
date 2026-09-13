# [M] Spoofed push notifications from malicious server

## Summary
Severity: Medium
Advisory: CVE-2024-39767
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2024-07-15
Source: https://osv.dev/vulnerability/CVE-2024-39767
Type: osv

## Details
Mattermost Mobile Apps versions <=2.16.0 fail to validate that the push notifications received for a server actually came from this serve that which allows a malicious server to send push notifications with another server’s diagnostic ID or server URL and have them show up in mobile apps as that server’s push notifications.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39767.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39767
