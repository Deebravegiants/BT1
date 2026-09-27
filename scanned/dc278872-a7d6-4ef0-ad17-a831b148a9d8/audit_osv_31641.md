# [M] Mobile crash via object that can't be cast to String in Attachment Field

## Summary
Severity: Medium
Advisory: CVE-2025-20630
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-16
Source: https://osv.dev/vulnerability/CVE-2025-20630
Type: osv

## Details
Mattermost Mobile versions <=2.22.0 fail to properly handle posts with attachments containing fields that cannot be cast to a String, which allows an attacker to cause the mobile to crash via creating and sending such a post to a channel.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/20xxx/CVE-2025-20630.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-20630
