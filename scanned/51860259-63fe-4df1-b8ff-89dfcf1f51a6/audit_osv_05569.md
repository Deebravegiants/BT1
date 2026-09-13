# [C] BIT-golang-2020-29510

## Summary
Severity: Critical
Advisory: BIT-golang-2020-29510
Aliases: CVE-2020-29510
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2020-29510
Type: osv

## Affected
- Bitnami: `golang` — affected >=0 <1.15.1

## Details
The encoding/xml package in Go versions 1.15 and earlier does not correctly preserve the semantics of directives during tokenization round-trips, which allows an attacker to craft inputs that behave in conflicting ways during different stages of processing in affected downstream applications.

## References
- https://github.com/mattermost/xml-roundtrip-validator/blob/master/advisories/unstable-directives.md
- https://security.netapp.com/advisory/ntap-20210129-0006/
- https://nvd.nist.gov/vuln/detail/CVE-2020-29510
