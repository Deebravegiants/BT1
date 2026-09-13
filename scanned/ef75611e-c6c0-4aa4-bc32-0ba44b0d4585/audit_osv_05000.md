# [M] BIT-gitlab-2020-26409

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-26409
Aliases: CVE-2020-26409
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-26409
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=0 <13.6.2

## Details
A DOS vulnerability exists in Gitlab CE/EE >=10.3, <13.4.7,>=13.5, <13.5.5,>=13.6, <13.6.2 that allows an attacker to trigger uncontrolled resource by bypassing input validation in markdown fields.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-26409.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/259626
- https://hackerone.com/reports/990461
- https://nvd.nist.gov/vuln/detail/CVE-2020-26409
