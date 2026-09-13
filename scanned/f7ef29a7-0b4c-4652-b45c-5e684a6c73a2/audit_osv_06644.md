# [M] BIT-mattermost-2024-45843

## Summary
Severity: Medium
Advisory: BIT-mattermost-2024-45843
Aliases: CVE-2024-45843
Ecosystem: Bitnami
Published: 2024-09-27
Source: https://osv.dev/vulnerability/BIT-mattermost-2024-45843
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=9.5.0 <9.5.9

## Details
Mattermost versions 9.5.x <= 9.5.8 fail to include the metadata endpoints of Oracle Cloud and Alibaba in the SSRF denylist, which allows an attacker to possibly cause an SSRF if Mattermost was deployed in Oracle Cloud or Alibaba.

## References
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2024-45843
