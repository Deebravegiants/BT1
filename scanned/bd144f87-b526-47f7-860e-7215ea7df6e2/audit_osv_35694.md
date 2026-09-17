# [M] RSA PKCS#1 verification skips last two hash bytes in NULL-omitted path

## Summary
Severity: Medium
Advisory: CVE-2026-12860
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/U:Amber)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-12860
Type: osv

## Details
In Bouncy Castle for Java before 1.85, RSA PKCS#1 verification skips last two hash bytes in NULL-omitted path. This issue also affects Bouncy Castle for Java LTS before 2.73.12.

## References
- https://www.bouncycastle.org/download/bouncy-castle-java-lts/
- https://www.bouncycastle.org/download/bouncy-castle-java/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12860.json
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%9012860
- https://nvd.nist.gov/vuln/detail/CVE-2026-12860
- https://github.com/bcgit/bc-java/commit/ea5970ea9b2fb91d763b904692fd21089ca3e396
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-lts-java
