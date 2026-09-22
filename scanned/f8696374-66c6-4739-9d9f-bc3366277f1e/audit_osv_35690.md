# [M] KCCMBlockCipher MAC does not bind nonce when AAD is absent (cross-nonce AEAD forgery)

## Summary
Severity: Medium
Advisory: CVE-2026-12803
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/U:Amber)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-12803
Type: osv

## Details
In Bouncy Castle for Java before 1.85, KCCMBlockCipher MAC does not bind nonce when AAD is absent (cross-nonce AEAD forgery). This issue also affects Bouncy Castle for Java LTS before 2.73.12.

## References
- https://www.bouncycastle.org/download/bouncy-castle-java-lts/
- https://www.bouncycastle.org/download/bouncy-castle-java/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12803.json
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%9012803
- https://nvd.nist.gov/vuln/detail/CVE-2026-12803
- https://github.com/bcgit/bc-java/commit/697794413ebf7bc5e3fce609a707826ba52981af
- https://github.com/bcgit/bc-java/commit/7d79aa76e984da85f2a541cae8ba2ae56e1713bc
- https://github.com/bcgit/bc-java
- https://github.com/bcgit/bc-lts-java
