# [M] Piwik (now Matomo) Reveals Sensitive Information by Accepting Input from `POST` Requests

## Summary
Severity: Medium
Advisory: GHSA-v8h8-93mx-82h5
CVE: CVE-2013-2633
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-v8h8-93mx-82h5
Type: github-advisory

## Affected
- Packagist: `matomo/matomo` — affected >=0 <1.11
- Packagist: `piwik/piwik` — affected >=0 <1.11

## Details
Piwik before 1.11 accepts input from a POST request instead of a GET request in unspecified circumstances, which might allow attackers to obtain sensitive information by leveraging the logging of parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2633
- https://github.com/matomo-org/matomo
- https://web.archive.org/web/20130313093839/http://piwik.org/blog/2013/03/piwik-1-11
