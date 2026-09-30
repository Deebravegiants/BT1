# [M] Operation on a Resource after Expiration or Termination in Kibana Leading to Unauthorized File Access

## Summary
Severity: Medium
Advisory: BIT-elk-2026-33463
Aliases: BIT-kibana-2026-33463, CVE-2026-33463
Ecosystem: Bitnami
Published: 2026-06-01
Source: https://osv.dev/vulnerability/BIT-elk-2026-33463
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.0.0 <9.3.5

## Details
Operation on a Resource after Expiration or Termination (CWE-672) in Kibana can lead to unauthorized information disclosure. A logic error in how expiration timestamps were validated allowed a time-bounded access token to remain usable beyond its intended validity window, enabling an unauthenticated actor in possession of the token to retrieve the associated content after expiration.

## References
- https://discuss.elastic.co/t/8-19-16-9-3-5-security-update-esa-2026-33/386551
- https://nvd.nist.gov/vuln/detail/CVE-2026-33463
