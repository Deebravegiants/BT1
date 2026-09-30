# [C] BIT-gitlab-2020-13347

## Summary
Severity: Critical
Advisory: BIT-gitlab-2020-13347
Aliases: CVE-2020-13347
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13347
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.4.0 <13.4.1

## Details
A command injection vulnerability was discovered in Gitlab runner versions prior to 13.2.4, 13.3.2 and 13.4.1. When the runner is configured on a Windows system with a docker executor, which allows the attacker to run arbitrary commands on Windows host, via DOCKER_AUTH_CONFIG build variable.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13347.json
- https://gitlab.com/gitlab-org/gitlab-runner/-/issues/26725
- https://hackerone.com/reports/955016
- https://nvd.nist.gov/vuln/detail/CVE-2020-13347
