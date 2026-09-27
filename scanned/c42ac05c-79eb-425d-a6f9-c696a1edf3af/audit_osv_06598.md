# [H] BIT-mattermost-2020-14453

## Summary
Severity: High
Advisory: BIT-mattermost-2020-14453
Aliases: CVE-2020-14453
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2020-14453
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=0 <5.21.0

## Details
An issue was discovered in Mattermost Server before 5.21.0. Socket read operations are not appropriately restricted, which allows attackers to cause a denial of service, aka MMSA-2020-0005.

## References
- https://mattermost.com/security-updates/
- https://nvd.nist.gov/vuln/detail/CVE-2020-14453
