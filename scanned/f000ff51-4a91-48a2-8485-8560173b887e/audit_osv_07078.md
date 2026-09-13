# [C] NGINX Map directive and Regex matching vulnerability

## Summary
Severity: Critical
Advisory: BIT-nginx-2026-42533
Aliases: BIT-nginx-gateway-2026-42533, CVE-2026-42533
Ecosystem: Bitnami
Published: 2026-07-20
Source: https://osv.dev/vulnerability/BIT-nginx-2026-42533
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.31.0 <1.31.3

## Details
A vulnerability exists in NGINX Plus and NGINX Open Source when a map directive uses regex matching and a string expression references the map's regex capture variables before referencing the map output variable. Alternatively, the same result could be achieved by using a non-cacheable variable in a string expression under certain conditions. An unauthenticated attacker along with conditions beyond their control can exploit this vulnerability by sending crafted HTTP requests. This may cause a heap buffer overflow in the NGINX worker process leading to a restart. Additionally, attackers can execute code on systems with Address Space Layout Randomization (ASLR) disabled or when the attacker can bypass ASLR.

Impact:
This vulnerability may allow remote attackers to cause a denial-of-service (DoS) on the NGINX system or to possibly trigger a code execution. There is no control plane exposure; this is a data plane issue only.




 Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000162097
- https://nvd.nist.gov/vuln/detail/CVE-2026-42533
