# [M] Deserialization of Untrusted Data in Flask-Caching

## Summary
Severity: Medium
Advisory: GHSA-656c-6cxf-hvcv
CVE: CVE-2021-33026
CWE: CWE-269, CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-06-18
Source: https://github.com/advisories/GHSA-656c-6cxf-hvcv
Type: github-advisory

## Affected
- PyPI: `Flask-Caching` — affected >=0

## Details
Flask-Cache adds easy cache support to Flask. The Flask-Caching extension through 1.10.1 for Flask relies on Pickle for serialization, which may lead to remote code execution or local privilege escalation. If an attacker gains access to cache storage (e.g., filesystem, Memcached, Redis, etc.), they can construct a crafted payload, poison the cache, and execute Python code.

However, this is not a high-severity issue, as for an attack like this to work, an attacker must:

1. Be able to write arbitrary values to the cache
2. Be able to generate a cache key that will collide with a value being read by the application
3. Cause the application to read a maliciously-injected value

Any situation where all 3 of those is true is a situation where the application has larger problems; for example, if someone's able to inject malicious cached rendered pages into a Flask app's cache, then they can make the website say literally anything they want, regardless of whether it involves the execution of remote code. Basically, the Pickle vulnerability follows from a website already being extremely vulnerable (due to conditions 1 and 2 being met).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33026
- https://github.com/pallets-eco/flask-caching/pull/209#issuecomment-1136397937
- https://github.com/sh4nks/flask-caching/pull/209
- https://github.com/advisories/GHSA-656c-6cxf-hvcv
- https://github.com/pypa/advisory-database/tree/main/vulns/flask-caching/PYSEC-2021-13.yaml
- https://github.com/sh4nks/flask-caching
