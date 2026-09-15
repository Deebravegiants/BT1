# [H] Accessing Untrusted Directory May Allow Local Privilege Escalation

## Summary
Severity: High
Advisory: BIT-mongodb-2024-7553
Aliases: CVE-2024-7553
Ecosystem: Bitnami
Published: 2024-09-20
Source: https://osv.dev/vulnerability/BIT-mongodb-2024-7553
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=7.0.0 <7.0.12

## Details
Incorrect validation of files loaded from a local untrusted directory may allow local privilege escalation if the underlying operating systems is Windows. This may result in the application executing arbitrary behaviour determined by the contents of untrusted files. This issue affects MongoDB Server v5.0 versions prior to 5.0.27, MongoDB Server v6.0 versions prior to 6.0.16, MongoDB Server v7.0 versions prior to 7.0.12, MongoDB Server v7.3 versions prior 7.3.3, MongoDB C Driver versions prior to 1.26.2 and MongoDB PHP Driver versions prior to 1.18.1.

Required Configuration:

Only environments with Windows as the underlying operating system is affected by this issue

## References
- https://jira.mongodb.org/browse/CDRIVER-5650
- https://jira.mongodb.org/browse/PHPC-2369
- https://jira.mongodb.org/browse/SERVER-93211
- https://nvd.nist.gov/vuln/detail/CVE-2024-7553
