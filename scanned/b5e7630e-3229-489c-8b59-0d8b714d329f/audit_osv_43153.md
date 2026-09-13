# [M] Instatic - Cache Poisoning via Unauthenticated Server Island Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-72587
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72587
Type: osv

## Details
A cache poisoning vulnerability in CoreBunch/Instatic through 0.0.14 allows an unauthenticated remote attacker to poison the shared process-wide render cache by manipulating the u query parameter of the GET /_instatic/hole/<nodeId> server island endpoint.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72587.json
- https://github.com/CoreBunch/Instatic
- https://nvd.nist.gov/vuln/detail/CVE-2026-72587
