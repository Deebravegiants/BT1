# [H] OS Command Injection in celery

## Summary
Severity: High
Advisory: GHSA-q4xr-rc97-m4xx
CVE: CVE-2021-23727
CWE: CWE-77, CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-q4xr-rc97-m4xx
Type: github-advisory

## Affected
- PyPI: `celery` — affected >=0 <5.2.2

## Details
This affects the package celery before 5.2.2. It by default trusts the messages and metadata stored in backends (result stores). When reading task metadata from the backend, the data is deserialized. Given that an attacker can gain access to, or somehow manipulate the metadata within a celery backend, they could trigger a stored command injection vulnerability and potentially gain further access to the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23727
- https://github.com/celery/celery/commit/1f7ad7e6df1e02039b6ab9eec617d283598cad6b
- https://github.com/advisories/GHSA-q4xr-rc97-m4xx
- https://github.com/celery/celery
- https://github.com/celery/celery/blob/master/Changelog.rst%23522
- https://github.com/pypa/advisory-database/tree/main/vulns/celery/PYSEC-2021-858.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SYXRGHWHD2WWMHBWCVD5ULVINPKNY3P5
- https://snyk.io/vuln/SNYK-PYTHON-CELERY-2314953
