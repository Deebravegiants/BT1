# [M] pretix potential IP address spoofing vulnerability

## Summary
Severity: Medium
Advisory: GHSA-j9gq-w73w-9h6c
CVE: CVE-2023-44463
CWE: CWE-290
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-10-02
Source: https://github.com/advisories/GHSA-j9gq-w73w-9h6c
Type: github-advisory

## Affected
- PyPI: `pretix` — affected >=0 <2023.7.1

## Details
An issue was discovered in pretix before 2023.7.1. Incorrect parsing of configuration files causes the application to trust unchecked X-Forwarded-For headers even though it has not been configured to do so. This can lead to IP address spoofing by users of the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-44463
- https://github.com/pretix/pretix/commit/ccdce2ccb8207b82501af3c03f50abc0f819b469
- https://github.com/pretix/pretix
- https://github.com/pretix/pretix/compare/v2023.7.0...v2023.7.1
- https://github.com/pretix/pretix/tags
- https://github.com/pypa/advisory-database/tree/main/vulns/pretix/PYSEC-2023-187.yaml
- https://pretix.eu/about/en/blog/20230911-release-2023-7-1
- https://pretix.eu/about/en/ticketing
