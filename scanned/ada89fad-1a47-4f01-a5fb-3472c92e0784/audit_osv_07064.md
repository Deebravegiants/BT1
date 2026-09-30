# [M] NGINX Unit Java Vulnerability

## Summary
Severity: Medium
Advisory: BIT-nginx-2025-1695
Aliases: CVE-2025-1695
Ecosystem: Bitnami
Published: 2025-03-06
Source: https://osv.dev/vulnerability/BIT-nginx-2025-1695
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.29.1

## Details
In NGINX Unit before version 1.34.2 with the Java Language Module in use, undisclosed requests can lead to an infinite loop and cause an increase in CPU resource utilization.  This vulnerability allows a remote attacker to cause a degradation that can lead to a limited denial-of-service (DoS).  There is no control plane exposure; this is a data plane issue only.  Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000149959
- https://nvd.nist.gov/vuln/detail/CVE-2025-1695
