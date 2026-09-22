# [C] jsrsasign: Incomplete Comparison Allows DSA Private Key Recovery via Biased Nonce Generation

## Summary
Severity: Critical
Advisory: GHSA-5jx8-q4cp-rhh6
CVE: CVE-2026-4599
CWE: CWE-1023, CWE-338
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-5jx8-q4cp-rhh6
Type: github-advisory

## Affected
- npm: `jsrsasign` — affected >=7.0.0 <11.1.1

## Details
Versions of the package jsrsasign from 7.0.0 and before 11.1.1 are vulnerable to Incomplete Comparison with Missing Factors via the getRandomBigIntegerZeroToMax and getRandomBigIntegerMinToMax functions in src/crypto-1.1.js; an attacker can recover the private key by exploiting the incorrect compareTo checks that accept out-of-range candidates and thus bias DSA nonces during signature generation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4599
- https://github.com/kjur/jsrsasign/pull/647
- https://github.com/kjur/jsrsasign/commit/ee4b013478366cb16cea9a4bdfb218b6077f83b1
- https://security.snyk.io/vuln/SNYK-JS-JSRSASIGN-15370939
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-15812264
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-4599.json
- https://github.com/kjur/jsrsasign
- https://gist.github.com/Kr0emer/081681818b51605c91945126d74b4f20
- https://bugzilla.redhat.com/show_bug.cgi?id=2450207
- https://access.redhat.com/security/cve/CVE-2026-4599
- https://access.redhat.com/errata/RHSA-2026:6926
- https://access.redhat.com/errata/RHSA-2026:6912
- https://access.redhat.com/errata/RHSA-2026:6720
- https://access.redhat.com/errata/RHSA-2026:6568
- https://access.redhat.com/errata/RHSA-2026:19410
- https://access.redhat.com/errata/RHSA-2026:19409
- https://access.redhat.com/errata/RHSA-2026:19375
