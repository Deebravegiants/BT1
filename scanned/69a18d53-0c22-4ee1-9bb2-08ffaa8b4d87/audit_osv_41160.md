# [M] CCM-family modes write plaintext to caller buffer before tag check

## Summary
Severity: Medium
Advisory: CVE-2026-58061
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/U:Amber)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-58061
Type: osv

## Details
In Bouncy Castle for Java before 1.85, CCM-family modes write plaintext to caller buffer before tag check. This issue also affects Bouncy Castle for Java LTS before 2.73.12, and Bouncy Castle for Java FIPS (BC-FJA) before bc-fips 1.0.2.7 (1.0.X series), 2.0.2 (2.0.X series) and 2.1.3 (2.1.X series).

## References
- https://www.bouncycastle.org/download/bouncy-castle-java-fips/
- https://www.bouncycastle.org/download/bouncy-castle-java-lts/
- https://www.bouncycastle.org/download/bouncy-castle-java/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58061.json
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%9058061
- https://nvd.nist.gov/vuln/detail/CVE-2026-58061
- https://github.com/bcgit/bc-java/commit/08d675106bb663ddcc6ec0a4af6f6f62f512697b
- https://github.com/bcgit/bc-java/commit/cd4a5ab3ad619ff03c7767c1b8b19d5dea2970af
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-lts-java
