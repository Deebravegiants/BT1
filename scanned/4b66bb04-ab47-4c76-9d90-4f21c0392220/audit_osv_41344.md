# [H] MTI/A0 DH agreement exponentiates unvalidated peer value

## Summary
Severity: High
Advisory: CVE-2026-59650
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/U:Amber)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-59650
Type: osv

## Details
In Bouncy Castle for Java before 1.85, MTI/A0 DH agreement exponentiates unvalidated peer value. This issue also affects Bouncy Castle for Java LTS before 2.73.12.

## References
- https://www.bouncycastle.org/download/bouncy-castle-java-lts/
- https://www.bouncycastle.org/download/bouncy-castle-java/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59650.json
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%9059650
- https://nvd.nist.gov/vuln/detail/CVE-2026-59650
- https://github.com/bcgit/bc-java/commit/daeaae9d7075d04f40812e68671ebf4c777b5148
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-lts-java
