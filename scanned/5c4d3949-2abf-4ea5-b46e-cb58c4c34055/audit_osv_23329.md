# [H] CVE-2022-47925

## Summary
Severity: High
Advisory: CVE-2022-47925
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-27
Source: https://osv.dev/vulnerability/CVE-2022-47925
Type: osv

## Details
The validate JSON endpoint of the Secvisogram csaf-validator-service in versions < 0.1.0 processes tests with unexpected names. This insufficient input validation of requests by an unauthenticated remote user might lead to a partial DoS of the service. Only the request of the attacker is affected by this vulnerability.

## References
- https://wid.cert-bund.de/.well-known/csaf/white/2022/bsi-2022-0004.json
