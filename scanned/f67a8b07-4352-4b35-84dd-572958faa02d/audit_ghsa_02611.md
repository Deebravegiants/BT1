# [H] Parse Server crashes with query parameter

## Summary
Severity: High
Advisory: GHSA-xqp8-w826-hh6x
CVE: CVE-2021-39187
CWE: CWE-20, CWE-74, CWE-755
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-xqp8-w826-hh6x
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <4.10.3

## Details
### Impact
Parse Server crashes when if a query request contains an invalid value for the `explain` option. This is due to a bug in the MongoDB Node.js driver which throws an exception that Parse Server cannot catch.

### Patches
Upgrade to Parse Server 4.10.3

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-xqp8-w826-hh6x
- https://nvd.nist.gov/vuln/detail/CVE-2021-39187
- https://github.com/parse-community/parse-server/commit/308668c89474223e2448be92d6823b52c1c313ec
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/4.10.3
- https://jira.mongodb.org/browse/NODE-3463
