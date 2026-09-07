# [M] The Reporting Addon for CUBA Platform has Persistent XSS

## Summary
Severity: Medium
Advisory: GHSA-rff7-964g-pppx
CVE: CVE-2018-20663
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-rff7-964g-pppx
Type: github-advisory

## Affected
- Maven: `com.haulmont.cuba:cuba-web-toolkit` — affected >=6.10.0 <6.10.7
- Maven: `com.haulmont.cuba:cuba-web-toolkit` — affected >=6.9.0 <6.9.8
- Maven: `com.haulmont.cuba:cuba-web-toolkit` — affected >=0 <6.8.15

## Details
The Reporting Addon (aka Reports Addon) through 2019-01-02 for CUBA Platform through 6.10.x has Persistent XSS via the "Reports > Reports" name field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20663
- https://github.com/cuba-platform/cuba/issues/1741
- https://github.com/cuba-platform/reports/issues/140
- https://github.com/cuba-platform/cuba/commit/be6aa41ff36a365e2a995d37861e5acfcd32c2c5
- https://github.com/cuba-platform/cuba/commit/e9f972beeae42dc6dbc3aaa6b6ecc9814c0eedb4
- https://github.com/cuba-platform/cuba/commit/ec8784d8f596aa570604f4e5d5d4a7c3ae264c62
- https://github.com/cuba-platform/reports
