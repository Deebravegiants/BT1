# [M] TeamPass Stored Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-v969-5v7f-pmg2
CVE: CVE-2019-17205
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-v969-5v7f-pmg2
Type: github-advisory

## Affected
- Packagist: `nilsteampassnet/teampass` — affected >=0

## Details
TeamPass 2.1.27.36 allows Stored XSS by placing a payload in the username field during a login attempt. When an administrator looks at the log of failed logins, the XSS payload will be executed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17205
- https://github.com/nilsteampassnet/TeamPass/issues/2688
- https://github.com/nilsteampassnet/TeamPass/pull/2739/commits/ecdc6ca5a6e8c4b0b15d48f7e6327bf642fa6312
- https://github.com/nilsteampassnet/TeamPass
