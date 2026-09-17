# [C] Privilege Escalation due to Blind NoSQL Injection in flintcms

## Summary
Severity: Critical
Advisory: GHSA-jhq3-57xh-6643
CVE: CVE-2018-3783
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-08-21
Source: https://github.com/advisories/GHSA-jhq3-57xh-6643
Type: github-advisory

## Affected
- npm: `flintcms` — affected >=0 <1.1.10

## Details
Versions of `flintcms` before version 1.1.10 are vulnerable to account takeover due to blind MongoDB injection in the password reset.


## Recommendation

Update to version 1.1.10 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3783
- https://hackerone.com/reports/386807
- https://github.com/advisories/GHSA-jhq3-57xh-6643
- https://www.npmjs.com/advisories/689
