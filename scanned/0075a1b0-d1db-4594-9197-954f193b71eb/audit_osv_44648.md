# [C] Peppermint through 0.5.5 Use of Hard-coded JWT Signing Secret in docker-compose.yml

## Summary
Severity: Critical
Advisory: CVE-2026-85391
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85391
Type: osv

## Details
Peppermint through 0.5.5 contains a hardcoded JWT signing secret in docker-compose.yml that allows unauthenticated attackers to forge session tokens for any account. Attackers can use the published secret to mint valid tokens for arbitrary user IDs and access protected endpoints without credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85391.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85391
- https://www.vulncheck.com/advisories/peppermint-through-0.5.5-use-of-hard-coded-jwt-signing-secret-in-docker-compose-yml
- https://github.com/Peppermint-Lab/peppermint/issues/528
- https://github.com/Peppermint-Lab/peppermint
- https://github.com/Peppermint-Lab/peppermint/blob/0.5.5/apps/api/src/lib/jwt.ts
- https://github.com/Peppermint-Lab/peppermint/blob/0.5.5/docker-compose.yml
