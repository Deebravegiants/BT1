# [M] BIT-mattermost-2021-37863

## Summary
Severity: Medium
Advisory: BIT-mattermost-2021-37863
Aliases: CVE-2021-37863
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2021-37863
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=0 <6.0.1

## Details
Mattermost 6.0 and earlier fails to sufficiently validate parameters during post creation, which allows authenticated attackers to cause a client-side crash of the web application via a maliciously crafted post.

## References
- https://hackerone.com/reports/1253732
- https://mattermost.com/security-updates/
- https://nvd.nist.gov/vuln/detail/CVE-2021-37863
