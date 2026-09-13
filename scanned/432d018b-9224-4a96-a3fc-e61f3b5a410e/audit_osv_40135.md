# [H] CVE-2026-50107

## Summary
Severity: High
Advisory: CVE-2026-50107
Aliases: BIT-nginx-gateway-fabric-2026-50107
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-50107
Type: osv

## Details
When NGINX Plus or NGINX Open Source is configured as the data plane for NGINX Gateway Fabric, an injection vulnerability exists in the NGINX configuration generator component of NGINX Gateway Fabric. User-supplied string values from the NginxProxy Custom Resource Definition (CRD) access log format setting are rendered directly into NGINX configuration templates without sanitization or escaping. An authenticated attacker with permission to create or modify these CRDs may craft values that inject arbitrary NGINX configuration directives. This is a control plane issue; there is no data plane exposure from the vulnerability trigger itself. 


Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000161785
