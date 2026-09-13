# [H] Exposure of Sensitive Information to an Unauthorized Actor in Kibana Leading to Disclosure of Fleet Proxy Credentials

## Summary
Severity: High
Advisory: BIT-kibana-2026-72670
Aliases: BIT-elk-2026-72670, CVE-2026-72670
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-kibana-2026-72670
Type: osv

## Affected
- Bitnami: `kibana` — affected >=9.0.0 <9.4.5

## Details
A lower privileged user who holds only the privilege to read agent policies can read the entire configuration of a configured Fleet proxy. This would normally require the Fleet privilege to read settings.The proxy configuration possibly contains proxy authentication credentials and private key material that they should not be authorized to view.

## References
- https://discuss.elastic.co/t/kibana-8-19-20-and-9-4-5-security-update-esa-2026-87/389524
- https://nvd.nist.gov/vuln/detail/CVE-2026-72670
