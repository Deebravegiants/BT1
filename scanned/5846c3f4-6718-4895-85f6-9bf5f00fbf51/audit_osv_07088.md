# [M] NGINX Agent Vulnerability

## Summary
Severity: Medium
Advisory: BIT-nginx-agent-2024-7634
Aliases: CVE-2024-7634
Ecosystem: Bitnami
Published: 2025-12-03
Source: https://osv.dev/vulnerability/BIT-nginx-agent-2024-7634
Type: osv

## Affected
- Bitnami: `nginx-agent` — affected >=2.17.0 <2.37.0

## Details
NGINX Agent's "config_dirs" restriction feature allows a highly privileged attacker to gain the ability to write/overwrite files outside of the designated secure directory.

## References
- https://my.f5.com/manage/s/article/K000140630
- https://nvd.nist.gov/vuln/detail/CVE-2024-7634
