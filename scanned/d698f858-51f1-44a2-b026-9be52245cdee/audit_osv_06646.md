# [M] BIT-mattermost-2024-52032

## Summary
Severity: Medium
Advisory: BIT-mattermost-2024-52032
Aliases: CVE-2024-52032
Ecosystem: Bitnami
Published: 2024-11-15
Source: https://osv.dev/vulnerability/BIT-mattermost-2024-52032
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=9.11.0 <9.11.3, >=10.0.0

## Details
Mattermost versions 10.0.x <= 10.0.0 and 9.11.x <= 9.11.2 fail to properly query ElasticSearch when searching for the channel name in channel switcher which allows an attacker to get private channels names of channels that they are not a member of, when Elasticsearch v8 was enabled.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2024-52032
