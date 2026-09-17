# [M] OER parser recurses without depth limit on self-referential IEEE 1609.2 schema

## Summary
Severity: Medium
Advisory: CVE-2026-59645
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/U:Amber)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-59645
Type: osv

## Details
In Bouncy Castle for Java before 1.85, OER parser recurses without depth limit on self-referential IEEE 1609.2 schema. This issue also affects Bouncy Castle for Java LTS before 2.73.12, and Bouncy Castle for Java FIPS (BC-FJA) before bcutil-fips 2.0.7 (2.0.X series) and 2.1.7 (2.1.X series).

## References
- https://www.bouncycastle.org/download/bouncy-castle-java-fips/
- https://www.bouncycastle.org/download/bouncy-castle-java-lts/
- https://www.bouncycastle.org/download/bouncy-castle-java/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59645.json
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%9059645
- https://nvd.nist.gov/vuln/detail/CVE-2026-59645
- https://github.com/bcgit/bc-java/commit/822b2478b131097368a56290f5728e28dd042989
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-lts-java
