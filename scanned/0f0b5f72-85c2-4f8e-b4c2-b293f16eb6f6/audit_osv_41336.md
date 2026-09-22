# [M] CMS verifySignatures returns true for SignedData with zero signers

## Summary
Severity: Medium
Advisory: CVE-2026-59639
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/U:Amber)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-59639
Type: osv

## Details
In Bouncy Castle for Java before 1.85, CMS verifySignatures returns true for SignedData with zero signers. This issue also affects Bouncy Castle for Java LTS before 2.73.12, and Bouncy Castle for Java FIPS (BC-FJA) before bcpkix-fips 1.0.12 (1.0.X series), 2.0.12 (2.0.X series) and 2.1.12 (2.1.X series).

## References
- https://www.bouncycastle.org/download/bouncy-castle-java-fips/
- https://www.bouncycastle.org/download/bouncy-castle-java-lts/
- https://www.bouncycastle.org/download/bouncy-castle-java/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59639.json
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%9059639
- https://nvd.nist.gov/vuln/detail/CVE-2026-59639
- https://github.com/bcgit/bc-java/commit/99ddc6dcc6782e6a76b0dd587c77e62eb7096ad0
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-lts-java
