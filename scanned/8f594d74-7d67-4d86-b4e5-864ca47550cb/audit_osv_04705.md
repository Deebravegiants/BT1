# [H] Inefficient Regular Expression Complexity in Kibana Leading to Denial of Service

## Summary
Severity: High
Advisory: BIT-elk-2026-26936
Aliases: BIT-kibana-2026-26936, CVE-2026-26936
Ecosystem: Bitnami
Published: 2026-03-03
Source: https://osv.dev/vulnerability/BIT-elk-2026-26936
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.0.0 <9.2.5

## Details
Inefficient Regular Expression Complexity (CWE-1333) in the AI Inference Anonymization Engine in Kibana can lead Denial of Service via Regular Expression Exponential Blowup (CAPEC-492).

## References
- https://discuss.elastic.co/t/kibana-8-19-11-9-2-5-security-update-esa-2026-14/385250
- https://nvd.nist.gov/vuln/detail/CVE-2026-26936
