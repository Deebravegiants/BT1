# [H] BIT-mattermost-2022-0903

## Summary
Severity: High
Advisory: BIT-mattermost-2022-0903
Aliases: CVE-2022-0903
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2022-0903
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=6.3.0 <6.3.3

## Details
A call stack overflow bug in the SAML login feature in Mattermost server in versions up to and including 6.3.2 allows an attacker to crash the server via submitting a maliciously crafted POST body.

## References
- https://mattermost.com/security-updates/
- https://nvd.nist.gov/vuln/detail/CVE-2022-0903
