# [M] OpenPGP AEAD decryption skips final tag on chunk-aligned data

## Summary
Severity: Medium
Advisory: CVE-2026-12817
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/U:Amber)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-12817
Type: osv

## Details
In Bouncy Castle for Java before 1.85, OpenPGP AEAD decryption skips final tag on chunk-aligned data. This issue also affects Bouncy Castle for Java LTS before 2.73.12, and Bouncy Castle for Java FIPS (BC-FJA) before bcpg-fips 1.0.13 (1.0.X series), 2.0.13 (2.0.X series) and 2.1.13 (2.1.X series).

## References
- https://www.bouncycastle.org/download/bouncy-castle-java-fips/
- https://www.bouncycastle.org/download/bouncy-castle-java-lts/
- https://www.bouncycastle.org/download/bouncy-castle-java/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12817.json
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%9012817
- https://nvd.nist.gov/vuln/detail/CVE-2026-12817
- https://github.com/bcgit/bc-java/commit/4b712819846ec944379f4909101abac20f0ad4b0
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-lts-java
