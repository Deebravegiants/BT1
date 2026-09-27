# [H] NGINX Gateway Fabric vulnerability

## Summary
Severity: High
Advisory: BIT-nginx-gateway-fabric-2026-11311
Aliases: CVE-2026-11311
Ecosystem: Bitnami
Published: 2026-06-24
Source: https://osv.dev/vulnerability/BIT-nginx-gateway-fabric-2026-11311
Type: osv

## Affected
- Bitnami: `nginx-gateway-fabric` — affected >=2.5.0 <2.6.4

## Details
When NGINX Plus is configured as the data plane for NGINX Gateway Fabric, an injection vulnerability exists in the NGINX configuration generator component of NGINX Gateway Fabric. User-supplied string values from the NginxProxy Custom Resource Definition serverTokens field and the AuthenticationFilter Custom Resource Definition extraAuthArgs field are rendered directly into NGINX configuration templates without sanitization or escaping. An authenticated attacker with permission to create or modify these Custom Resource Definitions may craft values that inject arbitrary NGINX configuration directives. This is a control plane issue; there is no data plane exposure from the vulnerability trigger itself. 


Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000161611
- https://nvd.nist.gov/vuln/detail/CVE-2026-11311
