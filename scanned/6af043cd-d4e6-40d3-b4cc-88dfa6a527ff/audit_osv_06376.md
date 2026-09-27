# [C] BIT-limesurvey-2020-11455

## Summary
Severity: Critical
Advisory: BIT-limesurvey-2020-11455
Aliases: CVE-2020-11455
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-limesurvey-2020-11455
Type: osv

## Affected
- Bitnami: `limesurvey` — affected >=4.1.12 <4.1.13

## Details
LimeSurvey before 4.1.12+200324 contains a path traversal vulnerability in application/controllers/admin/LimeSurveyFileManager.php.

## References
- http://packetstormsecurity.com/files/157112/LimeSurvey-4.1.11-Path-Traversal.html
- https://github.com/LimeSurvey/LimeSurvey/commit/daf50ebb16574badfb7ae0b8526ddc5871378f1b
- https://www.exploit-db.com/exploits/48297
- https://nvd.nist.gov/vuln/detail/CVE-2020-11455
