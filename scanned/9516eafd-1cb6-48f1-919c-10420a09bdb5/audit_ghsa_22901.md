# [M] eGroupware Community Edition Stored XSS vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qfg7-wc25-r3j2
CVE: CVE-2017-14920
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qfg7-wc25-r3j2
Type: github-advisory

## Affected
- Packagist: `egroupware/egroupware` — affected >=0 <16.1.20170922

## Details
Stored XSS vulnerability in eGroupware Community Edition before 16.1.20170922 allows an unauthenticated remote attacker to inject JavaScript via the User-Agent HTTP header, which is mishandled during rendering by the application administrator.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-14920
- https://github.com/EGroupware/egroupware/commit/0ececf8c78f1c3f9ba15465f53a682dd7d89529f
- https://github.com/EGroupware/egroupware
- http://openwall.com/lists/oss-security/2017/09/28/12
