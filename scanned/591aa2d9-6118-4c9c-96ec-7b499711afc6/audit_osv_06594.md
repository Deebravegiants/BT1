# [H] BIT-mattermost-2020-14447

## Summary
Severity: High
Advisory: BIT-mattermost-2020-14447
Aliases: CVE-2020-14447
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2020-14447
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=0 <5.23.0

## Details
An issue was discovered in Mattermost Server before 5.23.0. Large webhook requests allow attackers to cause a denial of service (infinite loop), aka MMSA-2020-0021.

## References
- https://mattermost.com/security-updates/
- https://nvd.nist.gov/vuln/detail/CVE-2020-14447
