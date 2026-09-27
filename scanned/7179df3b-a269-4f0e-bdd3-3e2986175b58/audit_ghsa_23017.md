# [H] CodeIgniter HTTP Header Injection

## Summary
Severity: High
Advisory: GHSA-j9f9-8j39-4g97
CVE: CVE-2017-1000247
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-j9f9-8j39-4g97
Type: github-advisory

## Affected
- Packagist: `codeigniter4/framework` — affected >=3.1.3 <3.1.4

## Details
British Columbia Institute of Technology CodeIgniter 3.1.3 is vulnerable to HTTP Header Injection in the set_status_header() common function under Apache resulting in HTTP Header Injection flaws.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000247
- https://github.com/codeigniter4/framework
- https://www.codeigniter.com/userguide3/changelog.html#version-3-1-4
