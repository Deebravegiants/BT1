# [M] BIT-mattermost-2023-7113

## Summary
Severity: Medium
Advisory: BIT-mattermost-2023-7113
Aliases: CVE-2023-7113, GHSA-h3gq-j7p9-x3p4, GO-2024-2446
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2023-7113
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=0 <8.1.7

## Details
Mattermost version 8.1.6 and earlier fails to sanitize channel mention data in posts, which allows an attacker to inject markup in the web client.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2023-7113
