# [H] CVE-2026-55723

## Summary
Severity: High
Advisory: CVE-2026-55723
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-55723
Type: osv

## Details
When NGINX Ingress Controller is configured with Custom Resource Definitions (CRDs) or Ingress annotations, an injection vulnerability exists in the configuration generator of NGINX Ingress Controller. Multiple user-controllable fields are written into the generated NGINX configuration without sanitization. An authenticated attacker with permission to create or modify these CRDs or annotations may craft values that inject arbitrary NGINX configuration directives. 

Impact:
An authenticated attacker granted write access to NGINX Ingress Controller CRDs or Ingress annotations through the Kubernetes API may be able to inject arbitrary NGINX configuration directives, create or delete files, or disable services. There is no data plane exposure; this is a control plane issue only.

Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000161800
