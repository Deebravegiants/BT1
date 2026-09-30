# [M] Lazy ASN.1 sequence forcing resets nesting-depth guard

## Summary
Severity: Medium
Advisory: CVE-2026-13506
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/U:Amber)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-13506
Type: osv

## Details
In Bouncy Castle for Java before 1.85, Lazy ASN.1 sequence forcing resets nesting-depth guard. This issue also affects Bouncy Castle for Java LTS before 2.73.12, and Bouncy Castle for Java FIPS (BC-FJA) before bc-fips 1.0.2.7 (1.0.X series), 2.0.2 (2.0.X series) and 2.1.3 (2.1.X series).

## References
- https://www.bouncycastle.org/download/bouncy-castle-java-fips/
- https://www.bouncycastle.org/download/bouncy-castle-java-lts/
- https://www.bouncycastle.org/download/bouncy-castle-java/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13506.json
- https://github.com/bcgit/bc-java/wiki/CVE-2026-13506
- https://nvd.nist.gov/vuln/detail/CVE-2026-13506
- https://github.com/bcgit/bc-java/commit/77454da9b3dcaaa2991412d1c3c1a6e1a338ff84
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-lts-java
