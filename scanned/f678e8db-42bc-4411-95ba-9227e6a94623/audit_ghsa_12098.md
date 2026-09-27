# [H] jsrsasign: Negative Exponent Handling Leads to Signature Verification Bypass

## Summary
Severity: High
Advisory: GHSA-8qwj-4jxw-m8jw
CVE: CVE-2026-4602
CWE: CWE-681
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-8qwj-4jxw-m8jw
Type: github-advisory

## Affected
- npm: `jsrsasign` — affected >=0 <11.1.1

## Details
Versions of the package jsrsasign before 11.1.1 are vulnerable to Incorrect Conversion between Numeric Types due to handling negative exponents in ext/jsbn2.js. An attacker can force the computation of incorrect modular inverses and break signature verification by calling modPow with a negative exponent.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4602
- https://github.com/kjur/jsrsasign/pull/650
- https://github.com/kjur/jsrsasign/commit/5ea1c32bb2aa894b4bd29849839afe4f98728195
- https://security.snyk.io/vuln/SNYK-JS-JSRSASIGN-15371175
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-15812274
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-4602.json
- https://github.com/kjur/jsrsasign
- https://gist.github.com/Kr0emer/7ecd2be7d17419e4677315ef3758faf5
- https://bugzilla.redhat.com/show_bug.cgi?id=2450206
- https://access.redhat.com/security/cve/CVE-2026-4602
- https://access.redhat.com/errata/RHSA-2026:6926
- https://access.redhat.com/errata/RHSA-2026:6912
- https://access.redhat.com/errata/RHSA-2026:6720
- https://access.redhat.com/errata/RHSA-2026:6568
- https://access.redhat.com/errata/RHSA-2026:19410
- https://access.redhat.com/errata/RHSA-2026:19409
- https://access.redhat.com/errata/RHSA-2026:19375
