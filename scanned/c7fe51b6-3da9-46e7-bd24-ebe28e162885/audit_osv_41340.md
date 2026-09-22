# [M] OpenPGP inline-signature policy failures silently ignored

## Summary
Severity: Medium
Advisory: CVE-2026-59643
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/U:Amber)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-59643
Type: osv

## Details
In Bouncy Castle for Java before 1.85, OpenPGP inline-signature policy failures silently ignored. This issue also affects Bouncy Castle for Java FIPS (BC-FJA) before bcpg-fips 2.0.13.

## References
- https://www.bouncycastle.org/download/bouncy-castle-java-fips/
- https://www.bouncycastle.org/download/bouncy-castle-java/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59643.json
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%9059643
- https://nvd.nist.gov/vuln/detail/CVE-2026-59643
- https://github.com/bcgit/bc-java/commit/d3f8cc408b4a36d28e5a410c93436fe3d0fe726b
- https://github.com/bcgit/bc-java
