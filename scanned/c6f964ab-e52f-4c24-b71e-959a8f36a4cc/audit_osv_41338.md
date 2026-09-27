# [M] S/MIME validator trusts signer-asserted signingTime for path validation

## Summary
Severity: Medium
Advisory: CVE-2026-59641
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/U:Amber)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-59641
Type: osv

## Details
In Bouncy Castle for Java before 1.85, S/MIME validator trusts signer-asserted signingTime for path validation. This issue also affects Bouncy Castle for Java LTS before 2.73.12, and Bouncy Castle for Java FIPS (BC-FJA) before bcmail-fips and bcjmail-fips 1.0.7 (1.0.X series), 2.0.7 (2.0.X series) and 2.1.7 (2.1.X series).

## References
- https://www.bouncycastle.org/download/bouncy-castle-java-fips/
- https://www.bouncycastle.org/download/bouncy-castle-java-lts/
- https://www.bouncycastle.org/download/bouncy-castle-java/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59641.json
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%9059641
- https://nvd.nist.gov/vuln/detail/CVE-2026-59641
- https://github.com/bcgit/bc-java/commit/2f81b22d559b3a1b026388e1ca78dd547384def8
- https://github.com/bcgit/bc-java/commit/fd89fe918b37fea1c71e95fae50284a325b09721
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-lts-java
