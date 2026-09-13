# [C] Unescaped control characters in Gitblit

## Summary
Severity: Critical
Advisory: GHSA-fh55-vwjc-69c7
CVE: CVE-2022-31267
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-22
Source: https://github.com/advisories/GHSA-fh55-vwjc-69c7
Type: github-advisory

## Affected
- Maven: `com.gitblit:gitblit` — affected >=0 <1.9.3

## Details
Gitblit 1.9.2 allows privilege escalation via the Config User Service: a control character can be placed in a profile data field, such as an emailAddress%3Atext 'attacker@example.com\n\trole = "#admin"' value.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-31267
- https://github.com/gitblit/gitblit/issues/1410
- https://github.com/gitblit/gitblit/commit/9b4afad6f4be212474809533ec2c280cce86501a
- https://github.com/gitblit/gitblit
- https://github.com/gitblit/gitblit/releases/tag/v1.9.3
