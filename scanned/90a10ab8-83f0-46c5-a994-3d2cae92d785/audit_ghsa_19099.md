# [H] Hermes improperly validates a JWT

## Summary
Severity: High
Advisory: GHSA-vxm9-8mfw-vc6g
CVE: CVE-2025-1293
CWE: CWE-1390
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2025-02-20
Source: https://github.com/advisories/GHSA-vxm9-8mfw-vc6g
Type: github-advisory

## Affected
- Go: `github.com/hashicorp-forge/hermes` — affected >=0 <0.5.0

## Details
Hermes versions up to 0.4.0 improperly validated the JWT provided when using the AWS ALB authentication mode, potentially allowing for authentication bypass. This vulnerability, CVE-2025-1293, was fixed in Hermes 0.5.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-1293
- https://github.com/hashicorp-forge/hermes/commit/e36d479616099bd0c8dfde6786ea671f112d9106
- https://discuss.hashicorp.com/t/hcsec-2025-03-hashicorp-hermes-improperly-validates-aws-alb-jwts-which-may-lead-to-authentication-bypass/73371
- https://github.com/hashicorp-forge/hermes
