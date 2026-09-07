# [M] rdiffweb has insecure HTTP cookies

## Summary
Severity: Medium
Advisory: GHSA-m748-hjqg-rpp8
CVE: CVE-2022-3250
CWE: CWE-311, CWE-614
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-m748-hjqg-rpp8
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.4.6

## Details
In rdiffweb prior to version 2.4.6, the `cookie` session_id does not have a secure attribute when the URL is invalid. Version 2.4.6 contains a fix for the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3250
- https://github.com/ikus060/rdiffweb/commit/ac334dd27ceadac0661b1e2e059a8423433c3fee
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-287.yaml
- https://huntr.dev/bounties/39889a3f-8bb7-448a-b0d4-a18c671bbd23
