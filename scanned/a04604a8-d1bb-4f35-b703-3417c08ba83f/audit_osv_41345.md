# [M] BKS keystore accepts legacy version with 16-bit integrity MAC key

## Summary
Severity: Medium
Advisory: CVE-2026-59651
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/U:Amber)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-59651
Type: osv

## Details
In Bouncy Castle for Java before 1.85, BKS keystore accepts legacy version with 16-bit integrity MAC key. This issue also affects Bouncy Castle for Java LTS before 2.73.12.

## References
- https://www.bouncycastle.org/download/bouncy-castle-java-lts/
- https://www.bouncycastle.org/download/bouncy-castle-java/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59651.json
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%9059651
- https://nvd.nist.gov/vuln/detail/CVE-2026-59651
- https://github.com/bcgit/bc-java/commit/faf5daa6e9b8460f862afc0af1cc0da365f7d4d2
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-lts-java
