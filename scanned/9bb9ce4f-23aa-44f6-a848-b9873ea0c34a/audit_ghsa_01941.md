# [H] django-celery-results Stores Sensitive Information In Cleartext

## Summary
Severity: High
Advisory: GHSA-fvx8-v524-8579
CVE: CVE-2020-17495
CWE: CWE-312
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-06-04
Source: https://github.com/advisories/GHSA-fvx8-v524-8579
Type: github-advisory

## Affected
- PyPI: `django-celery-results` — affected >=0 <2.4.0

## Details
django-celery-results prior to 2.4.0 stores task results in the database. Among the data it stores are the variables passed into the tasks. The variables may contain sensitive cleartext information that does not belong unencrypted in the database.

In version 2.4.0 this is no longer the default behaviour but can be re-enabled with the `result_extended` flag in which case care should be taken to ensure any sensitive variables are scrubbed - see [here](https://github.com/celery/django-celery-results/issues/154#issuecomment-734706270) for an example.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-17495
- https://github.com/celery/django-celery-results/issues/142
- https://github.com/celery/django-celery-results/issues/154
- https://github.com/celery/django-celery-results/pull/316
- https://github.com/celery/django-celery-results/commit/ad508fe3433499e5fc94645412d911e174863f28
- https://github.com/advisories/GHSA-fvx8-v524-8579
- https://github.com/celery/django-celery-results
- https://github.com/pypa/advisory-database/tree/main/vulns/django-celery-results/PYSEC-2020-38.yaml
