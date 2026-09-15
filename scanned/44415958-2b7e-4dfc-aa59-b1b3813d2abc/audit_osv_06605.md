# [M] BIT-mattermost-2022-0904

## Summary
Severity: Medium
Advisory: BIT-mattermost-2022-0904
Aliases: CVE-2022-0904
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mattermost-2022-0904
Type: osv

## Affected
- Bitnami: `mattermost` — affected >=6.3.0 <6.3.3

## Details
A stack overflow bug in the document extractor in Mattermost Server in versions up to and including 6.3.2 allows an attacker to crash the server via submitting a maliciously crafted Apple Pages document.

## References
- https://mattermost.com/security-updates/
- https://nvd.nist.gov/vuln/detail/CVE-2022-0904
