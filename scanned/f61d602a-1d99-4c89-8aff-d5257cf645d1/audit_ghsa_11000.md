# [H] jsrsasign is vulnerable to DoS through Infinite Loop when processing zero or negative inputs

## Summary
Severity: High
Advisory: GHSA-8g7p-jf3g-gxcp
CVE: CVE-2026-4598
CWE: CWE-1287, CWE-835
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-8g7p-jf3g-gxcp
Type: github-advisory

## Affected
- npm: `jsrsasign` — affected >=0 <11.1.1

## Details
Versions of the package jsrsasign before 11.1.1 are vulnerable to Infinite loop via the bnModInverse function in ext/jsbn2.js when the BigInteger.modInverse implementation receives zero or negative inputs, allowing an attacker to hang the process permanently by supplying such crafted values (e.g., modInverse(0, m) or modInverse(-1, m)).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4598
- https://github.com/kjur/jsrsasign/pull/648
- https://github.com/kjur/jsrsasign/commit/ca5b027240287a1e71fe63019fc4400332594323
- https://security.snyk.io/vuln/SNYK-JS-JSRSASIGN-15370938
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-15812263
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-4598.json
- https://github.com/kjur/jsrsasign
- https://gist.github.com/Kr0emer/a1bf5cd4547cc630d2dcc5e761de8264
- https://bugzilla.redhat.com/show_bug.cgi?id=2450210
- https://access.redhat.com/security/cve/CVE-2026-4598
- https://access.redhat.com/errata/RHSA-2026:6720
- https://access.redhat.com/errata/RHSA-2026:6568
- https://access.redhat.com/errata/RHSA-2026:23361
- https://access.redhat.com/errata/RHSA-2026:22840
- https://access.redhat.com/errata/RHSA-2026:19410
- https://access.redhat.com/errata/RHSA-2026:19409
- https://access.redhat.com/errata/RHSA-2026:19375
