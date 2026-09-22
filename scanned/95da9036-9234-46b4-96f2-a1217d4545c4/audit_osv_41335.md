# [H] JSSE hostname verifier CN-fallback enabled by default despite documented opt-in

## Summary
Severity: High
Advisory: CVE-2026-59638
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/U:Amber)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-59638
Type: osv

## Details
In Bouncy Castle for Java before 1.85, JSSE hostname verifier CN-fallback enabled by default despite documented opt-in. This issue also affects Bouncy Castle for Java LTS before 2.73.12, and Bouncy Castle for Java FIPS (BC-FJA) before bctls-fips 1.0.24 (1.0.X series), 2.0.24 (2.0.X series) and 2.1.24 (2.1.X series).

## References
- https://www.bouncycastle.org/download/bouncy-castle-java-fips/
- https://www.bouncycastle.org/download/bouncy-castle-java-lts/
- https://www.bouncycastle.org/download/bouncy-castle-java/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59638.json
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%9059638
- https://nvd.nist.gov/vuln/detail/CVE-2026-59638
- https://github.com/bcgit/bc-java/commit/5ac55351cd1a8a7184d41c96a7ee87df0770240a
- https://github.com/bcgit/bc-java/commit/799bd15320a6310a447863638aa3df64acef829b
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-lts-java
