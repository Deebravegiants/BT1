# [M] BKS/UBER keystore allocates from untrusted lengths before integrity check

## Summary
Severity: Medium
Advisory: CVE-2026-12185
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/U:Amber)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-12185
Type: osv

## Details
In Bouncy Castle for Java before 1.85, BKS/UBER keystore allocates from untrusted lengths before integrity check. This issue also affects Bouncy Castle for Java LTS before 2.73.12.

## References
- https://www.bouncycastle.org/download/bouncy-castle-java-lts/
- https://www.bouncycastle.org/download/bouncy-castle-java/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12185.json
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%9012185
- https://nvd.nist.gov/vuln/detail/CVE-2026-12185
- https://github.com/bcgit/bc-java/commit/7bbd7fe5f44132e5b6140a2914435c12430eeb3d
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-lts-java
