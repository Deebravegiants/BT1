# [M] CVE-2022-47924

## Summary
Severity: Medium
Advisory: CVE-2022-47924
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-03-27
Source: https://osv.dev/vulnerability/CVE-2022-47924
Type: osv

## Details
An high privileged attacker may pass crafted arguments to the validate function of csaf-validator-lib of a locally installed Secvisogram in versions < 0.1.0 wich can result in arbitrary code execution and DoS once the users triggers the validation.

## References
- https://wid.cert-bund.de/.well-known/csaf/white/2022/bsi-2022-0004.json
