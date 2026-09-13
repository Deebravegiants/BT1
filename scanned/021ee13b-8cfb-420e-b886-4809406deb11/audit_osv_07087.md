# [M] NGINX Agent vulnerability CVE-2023-1550

## Summary
Severity: Medium
Advisory: BIT-nginx-agent-2023-1550
Aliases: CVE-2023-1550
Ecosystem: Bitnami
Published: 2025-12-03
Source: https://osv.dev/vulnerability/BIT-nginx-agent-2023-1550
Type: osv

## Affected
- Bitnami: `nginx-agent` — affected >=2.0.0 <2.23.3

## Details
Insertion of Sensitive Information into log file vulnerability in NGINX Agent. NGINX Agent version 2.0 before 2.23.3 inserts sensitive information into a log file. An authenticated attacker with local access to read agent log files may gain access to private keys. This issue is only exposed when the non-default trace level logging is enabled. Note: NGINX Agent is included with NGINX Instance Manager and used in conjunction with NGINX API Connectivity Manager, and NGINX Management Suite Security Monitoring.

## References
- https://my.f5.com/manage/s/article/K000133135
- https://nvd.nist.gov/vuln/detail/CVE-2023-1550
- https://security.netapp.com/advisory/ntap-20230511-0008/
