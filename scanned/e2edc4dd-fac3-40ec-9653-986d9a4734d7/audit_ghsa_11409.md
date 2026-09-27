# [H] jsrsasign: DSA signatures or X.509 certificates can be forged via DSA domain-parameter validation in KJUR.crypto.DSA.setPublic

## Summary
Severity: High
Advisory: GHSA-wvqx-v3f6-w8rh
CVE: CVE-2026-4600
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-wvqx-v3f6-w8rh
Type: github-advisory

## Affected
- npm: `jsrsasign` — affected >=0 <11.1.1

## Details
Versions of the package jsrsasign before 11.1.1 are vulnerable to Improper Verification of Cryptographic Signature via the DSA domain-parameter validation in KJUR.crypto.DSA.setPublic (and the related DSA/X509 verification flow in src/dsa-2.0.js). An attacker can forge DSA signatures or X.509 certificates that X509.verifySignature() accepts by supplying malicious domain parameters such as g=1, y=1, and a fixed r=1, which make the verification equation true for any hash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4600
- https://github.com/kjur/jsrsasign/pull/646
- https://github.com/kjur/jsrsasign/commit/37b4c06b145c7bfd6bc2a6df5d0a12c56b15ef60
- https://security.snyk.io/vuln/SNYK-JS-JSRSASIGN-15370940
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-15812268
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-4600.json
- https://github.com/kjur/jsrsasign
- https://gist.github.com/Kr0emer/bf15ddc097176e951659a24a8e9002a7
- https://bugzilla.redhat.com/show_bug.cgi?id=2450208
- https://access.redhat.com/security/cve/CVE-2026-4600
- https://access.redhat.com/errata/RHSA-2026:6926
- https://access.redhat.com/errata/RHSA-2026:6912
- https://access.redhat.com/errata/RHSA-2026:6720
- https://access.redhat.com/errata/RHSA-2026:6568
- https://access.redhat.com/errata/RHSA-2026:19410
- https://access.redhat.com/errata/RHSA-2026:19409
- https://access.redhat.com/errata/RHSA-2026:19375
