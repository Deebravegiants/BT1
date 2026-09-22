# [M] Multiple vulnerabilities in Limesurvey

## Summary
Severity: Medium
Advisory: BIT-limesurvey-2025-41076
Aliases: CVE-2025-41076
Ecosystem: Bitnami
Published: 2025-11-22
Source: https://osv.dev/vulnerability/BIT-limesurvey-2025-41076
Type: osv

## Affected
- Bitnami: `limesurvey` — affected >=6.13.0 <6.15.5

## Details
In version 6.13.0 of LimeSurvey, any external user can cause a 500 error in the survey system by sending a malformed session cookie. Instead of displaying a generic error message, the system exposes internal backend information, including the use of the Yii framework, the MySQL/MariaDB database engine, the table name 'lime_sessions', primary keys, and fragments of the content that caused the conflict. This information can simplify the collection of data about the internal architecture of the application by an attacker.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-41076
- https://www.incibe.es/en/incibe-cert/notices/aviso/multiple-vulnerabilities-limesurvey-0
