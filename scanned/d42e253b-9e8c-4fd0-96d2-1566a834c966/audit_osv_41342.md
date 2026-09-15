# [M] DTLS handshake reassembler allocates buffer from unchecked 24-bit length

## Summary
Severity: Medium
Advisory: CVE-2026-59646
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/U:Amber)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-59646
Type: osv

## Details
In Bouncy Castle for Java before 1.85, DTLS handshake reassembler allocates buffer from unchecked 24-bit length. This issue also affects Bouncy Castle for Java LTS before 2.73.12, and Bouncy Castle for Java FIPS (BC-FJA) before bctls-fips 1.0.24 (1.0.X series), 2.0.24 (2.0.X series) and 2.1.24 (2.1.X series).

## References
- https://www.bouncycastle.org/download/bouncy-castle-java-fips/
- https://www.bouncycastle.org/download/bouncy-castle-java-lts/
- https://www.bouncycastle.org/download/bouncy-castle-java/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59646.json
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%9059646
- https://nvd.nist.gov/vuln/detail/CVE-2026-59646
- https://github.com/bcgit/bc-java/commit/2d98721e71bbd822ffa0f84e088eea645cf679fa
- https://github.com/bcgit/bc-java/commit/2ea38942c7917f6d7ab4de93d8a5336d021df0d9
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-lts-java
