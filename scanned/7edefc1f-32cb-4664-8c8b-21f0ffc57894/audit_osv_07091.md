# [H] NGF vulnerability

## Summary
Severity: High
Advisory: BIT-nginx-gateway-fabric-2026-66362
Aliases: CVE-2026-66362
Ecosystem: Bitnami
Published: 2026-09-08
Source: https://osv.dev/vulnerability/BIT-nginx-gateway-fabric-2026-66362
Type: osv

## Affected
- Bitnami: `nginx-gateway-fabric` — affected >=2.5.0 <2.6.8

## Details
Description:
When NGINX Plus is configured as the data plane for NGINX Gateway Fabric, an injection vulnerability exists in the NGINX configuration generator component of NGINX Gateway Fabric. User-supplied string values from the Authentication Filter Custom Resource Definition clientID or cookieName fields, or in the clientSecret field of a Secret referenced by an Authentication Filter, are rendered directly into NGINX configuration templates without sanitization or escaping. 

Impact:
An authenticated attacker with permission to create or modify these resources may craft values that inject arbitrary NGINX configuration directives. This is a control plane issue; there is no data plane exposure.

## References
- https://my.f5.com/manage/s/article/K000162600
- https://nvd.nist.gov/vuln/detail/CVE-2026-66362
