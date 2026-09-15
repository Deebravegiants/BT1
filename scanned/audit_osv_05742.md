# [H] BIT-grafana-2023-4399

## Summary
Severity: High
Advisory: BIT-grafana-2023-4399
Aliases: CVE-2023-4399
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-grafana-2023-4399
Type: osv

## Affected
- Bitnami: `grafana` — affected >=10.1.0 <10.1.5

## Details
Grafana is an open-source platform for monitoring and observability. 

In Grafana Enterprise, Request security is a deny list that allows admins to configure Grafana in a way so that the instance doesn’t call specific hosts.

However, the restriction can be bypassed used punycode encoding of the characters in the request address.

## References
- https://grafana.com/security/security-advisories/cve-2023-4399/
- https://security.netapp.com/advisory/ntap-20231208-0003/
- https://nvd.nist.gov/vuln/detail/CVE-2023-4399
