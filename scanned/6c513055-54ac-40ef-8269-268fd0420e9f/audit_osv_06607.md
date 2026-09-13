# [M] BIT-mattermost-2022-3147

## Summary
Severity: Medium
Advisory: BIT-mattermost-2022-3147
Aliases: CVE-2022-3147
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2022-3147
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=0 <7.1.0

## Details
Mattermost version 7.0.x and earlier fails to sufficiently limit the in-memory sizes of concurrently uploaded JPEG images, which allows authenticated users to cause resource exhaustion on specific system configurations, resulting in server-side Denial of Service.

## References
- https://hackerone.com/reports/1549513
- https://mattermost.com/security-updates/
- https://nvd.nist.gov/vuln/detail/CVE-2022-3147
