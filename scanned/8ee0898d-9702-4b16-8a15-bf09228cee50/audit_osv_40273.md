# [M] CVE-2026-52865

## Summary
Severity: Medium
Advisory: CVE-2026-52865
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-52865
Type: osv

## Details
When NGINX Ingress Controller processes Ingress or TransportServer resources, an authenticated, remote attacker with permission to create or modify Ingress or TransportServer resources can cause the NGINX Ingress Controller process to terminate. 



Impact:
The NGINX Ingress Controller control plane process terminates and enters a persistent crash loop while the malformed Ingress or TransportServer resource remains in the cluster. This vulnerability allows a remote, authenticated attacker with at least Ingress or TransportServer resource write access to cause a denial-of-service (DoS) on the NGINX Ingress Controller system. There is no data plane exposure; this is a control plane issue only.

Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000161834
