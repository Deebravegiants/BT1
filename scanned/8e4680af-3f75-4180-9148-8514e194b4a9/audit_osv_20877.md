# [M] CVE-2021-37865

## Summary
Severity: Medium
Advisory: CVE-2021-37865
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-18
Source: https://osv.dev/vulnerability/CVE-2021-37865
Type: osv

## Details
Mattermost 6.2 and earlier fails to sufficiently process a specifically crafted GIF file when it is uploaded while drafting a post, which allows authenticated users to cause resource exhaustion while processing the file, resulting in server-side Denial of Service.

## References
- https://mattermost.com/security-updates/
- https://hackerone.com/reports/1428260
