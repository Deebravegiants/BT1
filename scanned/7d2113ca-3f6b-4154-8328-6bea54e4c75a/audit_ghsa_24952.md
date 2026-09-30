# [M] Celery local privilege escalation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rpc6-h455-3rx5
CVE: CVE-2011-4356
CWE: CWE-269
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-rpc6-h455-3rx5
Type: github-advisory

## Affected
- PyPI: `celery` — affected >=2.1.0 <2.2.8
- PyPI: `celery` — affected >=2.3.0 <2.3.4
- PyPI: `celery` — affected >=2.4.0 <2.4.4

## Details
Celery 2.1 and 2.2 before 2.2.8, 2.3 before 2.3.4, and 2.4 before 2.4.4 changes the effective id but not the real id during processing of the --uid and --gid arguments to celerybeat, celeryd_detach, celeryd-multi, and celeryev, which allows local users to gain privileges via vectors involving crafted code that is executed by the worker process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4356
- https://github.com/celery/celery/pull/544
- https://github.com/celery/celery/commit/53514b158b743678d8993638be5920cd09ccc35c
- https://github.com/celery/celery/commit/73388921731a0e6feb28ab0d389c4f7dc4d524f6
- https://github.com/celery/celery/commit/e0767e40994754fe8482bf4ff622c5c6d0b9f671
- https://github.com/celery/celery
- https://github.com/celery/celery/blob/master/docs/sec/CELERYSA-0001.txt
- https://github.com/pypa/advisory-database/tree/main/vulns/celery/PYSEC-2011-17.yaml
- https://web.archive.org/web/20140722114447/http://secunia.com/advisories/46973
- https://web.archive.org/web/20200305001706/http://www.securityfocus.com/bid/50825
