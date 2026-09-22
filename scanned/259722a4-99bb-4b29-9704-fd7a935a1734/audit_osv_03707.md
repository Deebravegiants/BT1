# [C] ALPINE-CVE-2026-42533

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-42533
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42533
Type: osv

## Affected
- Alpine:v3.21: `nginx` — affected >=0 <1.26.3-r2
- Alpine:v3.22: `nginx` — affected >=0 <1.28.3-r6
- Alpine:v3.23: `nginx` — affected >=0 <1.28.3-r6
- Alpine:v3.24: `nginx` — affected >=0 <1.30.4-r0

## Details
A vulnerability exists in NGINX Plus and NGINX Open Source when a map directive uses regex matching and a string expression references the map's regex capture variables before referencing the map output variable. Alternatively, the same result could be achieved by using a non-cacheable variable in a string expression under certain conditions. An unauthenticated attacker along with conditions beyond their control can exploit this vulnerability by sending crafted HTTP requests. This may cause a heap buffer overflow in the NGINX worker process leading to a restart. Additionally, attackers can execute code on systems with Address Space Layout Randomization (ASLR) disabled or when the attacker can bypass ASLR.

Impact:
This vulnerability may allow remote attackers to cause a denial-of-service (DoS) on the NGINX system or to possibly trigger a code execution. There is no control plane exposure; this is a data plane issue only.




 Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42533
