# [H] Sanitize-html Vulnerable To REDoS Attacks

## Summary
Severity: High
Advisory: GHSA-cgfm-xwp7-2cvr
CVE: CVE-2022-25887
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-31
Source: https://github.com/advisories/GHSA-cgfm-xwp7-2cvr
Type: github-advisory

## Affected
- npm: `sanitize-html` — affected >=0 <2.7.1

## Details
The package sanitize-html before 2.7.1 are vulnerable to Regular Expression Denial of Service (ReDoS) due to insecure global regular expression replacement logic of HTML comment removal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25887
- https://github.com/apostrophecms/sanitize-html/pull/557
- https://github.com/apostrophecms/sanitize-html/commit/b4682c12fd30e12e82fa2d9b766de91d7d2cd23c
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-3008102
- https://security.snyk.io/vuln/SNYK-JS-SANITIZEHTML-2957526
