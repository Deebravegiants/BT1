# [M] Kibana Allocation of Resources Without Limits or Throttling

## Summary
Severity: Medium
Advisory: BIT-elk-2025-68389
Aliases: BIT-kibana-2025-68389, CVE-2025-68389
Ecosystem: Bitnami
Published: 2025-12-20
Source: https://osv.dev/vulnerability/BIT-elk-2025-68389
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.2.0 <9.2.3

## Details
Allocation of Resources Without Limits or Throttling (CWE-770) in Kibana can allow a low-privileged authenticated user to cause Excessive Allocation (CAPEC-130) of computing resources and a denial of service (DoS) of the Kibana process via a crafted HTTP request.

## References
- https://discuss.elastic.co/t/kibana-8-19-9-9-1-9-and-9-2-3-security-update-esa-2025-36/384184
- https://nvd.nist.gov/vuln/detail/CVE-2025-68389
