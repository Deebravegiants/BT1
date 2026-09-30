# [H] Prototype Pollution Protection Bypass in qs

## Summary
Severity: High
Advisory: GHSA-gqgv-6jq5-jjj9
CVE: CVE-2017-1000048
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-04-30
Source: https://github.com/advisories/GHSA-gqgv-6jq5-jjj9
Type: github-advisory

## Affected
- npm: `qs` — affected >=0 <6.0.4
- npm: `qs` — affected >=6.1.0 <6.1.2
- npm: `qs` — affected >=6.2.0 <6.2.3
- npm: `qs` — affected >=6.3.0 <6.3.2

## Details
Affected version of `qs` are vulnerable to Prototype Pollution because it is possible to bypass the protection. The `qs.parse` function fails to properly prevent an object's prototype to be altered when parsing arbitrary input. Input containing `[` or `]` may bypass the prototype pollution protection and alter the Object prototype. This allows attackers to override properties that will exist in all objects, which may lead to Denial of Service or Remote Code Execution in specific circumstances.


## Recommendation

Upgrade to 6.0.4, 6.1.2, 6.2.3, 6.3.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000048
- https://github.com/ljharb/qs/issues/200
- https://github.com/ljharb/qs/commit/beade029171b8cef9cee0d03ebe577e2dd84976d
- https://access.redhat.com/errata/RHSA-2017:2672
- https://github.com/ljharb/qs
- https://snyk.io/vuln/npm:qs:20170213
- https://www.npmjs.com/advisories/1469
