# [M] HSS public-key level count unbounded, enabling huge allocation on verify

## Summary
Severity: Medium
Advisory: CVE-2026-58060
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/U:Amber)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-58060
Type: osv

## Details
In Bouncy Castle for Java before 1.85, HSS public-key level count unbounded, enabling huge allocation on verify. This issue also affects Bouncy Castle for Java LTS before 2.73.12, and Bouncy Castle for Java FIPS (BC-FJA) before bc-fips 2.0.2 (2.0.X series) and 2.1.3 (2.1.X series).

## References
- https://www.bouncycastle.org/download/bouncy-castle-java-fips/
- https://www.bouncycastle.org/download/bouncy-castle-java-lts/
- https://www.bouncycastle.org/download/bouncy-castle-java/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58060.json
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%9058060
- https://nvd.nist.gov/vuln/detail/CVE-2026-58060
- https://github.com/bcgit/bc-java/commit/311cabbb6fcead7647fec16681423a4439118276
- https://github.com/bcgit/bc-java/commit/6c9f30b3fdaa3f2140809278caebbffc55920922
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-lts-java
