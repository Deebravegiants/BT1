# [H] BIT-redmine-2022-44030

## Summary
Severity: High
Advisory: BIT-redmine-2022-44030
Aliases: CVE-2022-44030
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-redmine-2022-44030
Type: osv

## Affected
- Bitnami: `redmine` — affected >=5.0.0 <5.0.4

## Details
Redmine 5.x before 5.0.4 allows downloading of file attachments of any Issue or any Wiki page due to insufficient permission checks. Depending on the configuration, this may require login as a registered user.

## References
- https://www.redmine.org/news/139
- https://www.redmine.org/projects/redmine/wiki/Security_Advisories
- https://nvd.nist.gov/vuln/detail/CVE-2022-44030
