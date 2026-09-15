# [M] BIT-mattermost-2021-37862

## Summary
Severity: Medium
Advisory: BIT-mattermost-2021-37862
Aliases: CVE-2021-37862
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2021-37862
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=0 <6.0.1

## Details
Mattermost 6.0 and earlier fails to sufficiently validate the email address during registration, which allows attackers to trick users into signing up using attacker-controlled email addresses via crafted invitation token.

## References
- https://hackerone.com/reports/1357013
- https://mattermost.com/security-updates/
- https://nvd.nist.gov/vuln/detail/CVE-2021-37862
