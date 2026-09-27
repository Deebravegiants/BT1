# [M] NGINX Agent Vulnerability

## Summary
Severity: Medium
Advisory: BIT-nginx-agent-2026-60062
Aliases: CVE-2026-60062
Ecosystem: Bitnami
Published: 2026-07-20
Source: https://osv.dev/vulnerability/BIT-nginx-agent-2026-60062
Type: osv

## Affected
- Bitnami: `nginx-agent` — affected >=2.37.0 <2.47.0

## Details
The NGINX Agent config_dirs directive allows a low-privileged attacker to gain limited read and write access to files outside of the designated secure directory. The config_dirs directive required for this issue can also be configured through NGINX Instance Manager. A successful exploit may allow an attacker to cross a security boundary.

Impact:
A remotely authenticated low-privileged attacker could gain limited read and write access outside of the list of directories specified in the NGINX Agent configuration.



Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000161971
- https://nvd.nist.gov/vuln/detail/CVE-2026-60062
