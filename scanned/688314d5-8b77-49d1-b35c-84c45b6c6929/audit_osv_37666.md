# [M] CVE-2026-32682

## Summary
Severity: Medium
Advisory: CVE-2026-32682
Aliases: BIT-nginx-gateway-fabric-2026-32682
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-32682
Type: osv

## Details
When NGINX Gateway Fabric is configured using GRPCRoutes, an authenticated, remote attacker with permission to create or modify GRPCRoute resources can cause the NGINX Gateway Fabric control plane to terminate by sending undisclosed GRPCRoute configurations containing backendRef filters. 


Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000161786
