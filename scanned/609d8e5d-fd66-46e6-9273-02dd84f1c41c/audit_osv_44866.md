# [H] Name Constraints bypass via trailing dot in rfc822Name and URI

## Summary
Severity: High
Advisory: CVE-2026-8763
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/U:Amber)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-8763
Type: osv

## Details
In Bouncy Castle for Java before 1.85, Name Constraints bypass via trailing dot in rfc822Name and URI. This issue also affects Bouncy Castle for Java LTS before 2.73.12, and Bouncy Castle for Java FIPS (BC-FJA) before bc-fips 1.0.2.7 (1.0.X series), 2.0.2 (2.0.X series) and 2.1.3 (2.1.X series).

## References
- https://www.bouncycastle.org/download/bouncy-castle-java-fips/
- https://www.bouncycastle.org/download/bouncy-castle-java-lts/
- https://www.bouncycastle.org/download/bouncy-castle-java/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8763.json
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%908763
- https://nvd.nist.gov/vuln/detail/CVE-2026-8763
- https://github.com/bcgit/bc-java/commit/2c28b253a44681fbbc562561eab6ad383d2ae558
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-lts-java
