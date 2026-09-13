# [H] Stapled OCSP response accepted without binding to the checked certificate

## Summary
Severity: High
Advisory: CVE-2026-58062
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/U:Amber)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-58062
Type: osv

## Details
In Bouncy Castle for Java before 1.85, Stapled OCSP response accepted without binding to the checked certificate. This issue also affects Bouncy Castle for Java LTS before 2.73.12, and Bouncy Castle for Java FIPS (BC-FJA) before bc-fips 2.0.2 (2.0.X series) and 2.1.3 (2.1.X series).

## References
- https://www.bouncycastle.org/download/bouncy-castle-java-fips/
- https://www.bouncycastle.org/download/bouncy-castle-java-lts/
- https://www.bouncycastle.org/download/bouncy-castle-java/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58062.json
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%9058062
- https://nvd.nist.gov/vuln/detail/CVE-2026-58062
- https://github.com/bcgit/bc-java/commit/add5f822660f3b2c29fd824e2f4095469c42a1c7
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-lts-java
