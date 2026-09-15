# [M] Possible OOM from unbounded up-front allocation on a definite-length read

## Summary
Severity: Medium
Advisory: CVE-2026-14682
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/U:Amber)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-14682
Type: osv

## Details
In Bouncy Castle for Java before 1.85, Possible OOM from unbounded up-front allocation on a definite-length read. This issue also affects Bouncy Castle for Java LTS before 2.73.12, and Bouncy Castle for Java FIPS (BC-FJA) before bc-fips 1.0.2.7 (1.0.X series), 2.0.2 (2.0.X series) and 2.1.3 (2.1.X series), and before bctls-fips 1.0.24.

## References
- https://www.bouncycastle.org/download/bouncy-castle-java-fips/
- https://www.bouncycastle.org/download/bouncy-castle-java-lts/
- https://www.bouncycastle.org/download/bouncy-castle-java/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14682.json
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%9014682
- https://nvd.nist.gov/vuln/detail/CVE-2026-14682
- https://github.com/bcgit/bc-java/commit/37094e504ef50cf9ce4e0fb9e5105d495ff5c2d2
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-lts-java
