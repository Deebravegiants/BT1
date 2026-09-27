# [C] Incorrect Authorization in GitLab

## Summary
Severity: Critical
Advisory: BIT-gitlab-2023-5009
Aliases: CVE-2023-5009
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-5009
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.3.0 <16.3.4

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 13.12 before 16.2.7, all versions starting from 16.3 before 16.3.4. It was possible for an attacker to run pipeline jobs as an arbitrary user via scheduled security scan policies. This was a bypass of [CVE-2023-3932](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-3932) showing additional impact.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/425304
- https://hackerone.com/reports/2147126
- https://nvd.nist.gov/vuln/detail/CVE-2023-5009
