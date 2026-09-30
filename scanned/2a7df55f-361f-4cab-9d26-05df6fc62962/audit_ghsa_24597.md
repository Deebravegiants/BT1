# [C] OHDSI WebAPI vulnerable to SQL Injection

## Summary
Severity: Critical
Advisory: GHSA-2chv-87wj-pjv2
CVE: CVE-2019-15563
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2chv-87wj-pjv2
Type: github-advisory

## Affected
- Maven: `org.ohdsi:WebAPI` — affected >=0 <2.7.2

## Details
Observational Health Data Sciences and Informatics (OHDSI) WebAPI before 2.7.2 allows SQL injection in `FeatureExtractionService.java`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15563
- https://github.com/OHDSI/WebAPI/pull/1101
- https://github.com/OHDSI/WebAPI/commit/d7b12b2f5234e425e5bc76545e75de0d6eb3f8fd
- https://github.com/OHDSI/WebAPI
- https://github.com/OHDSI/WebAPI/milestone/28?closed=1
- https://github.com/OHDSI/WebAPI/releases/tag/v2.7.2
