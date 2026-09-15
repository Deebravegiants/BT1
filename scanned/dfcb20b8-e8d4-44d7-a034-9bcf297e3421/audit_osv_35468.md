# [M] Garbage collection can delay for AES CBC Native support, resulting in heap exhaustion

## Summary
Severity: Medium
Advisory: CVE-2025-9341
Aliases: GHSA-jfcv-jv9g-2vx2
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/S:P/AU:N/R:U/V:C/RE:M/U:Amber)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-9341
Type: osv

## Details
Uncontrolled Resource Consumption vulnerability in Legion of the Bouncy Castle Inc. Bouncy Castle for Java FIPS bc-fips on All (API modules), Legion of the Bouncy Castle Inc. Bouncy Castle for Java LTS bcprov-lts8on on All (API modules) allows Excessive Allocation. This vulnerability is associated with program files org/bouncycastle/crypto/fips/AESNativeCBC.Java, org/bouncycastle/crypto/engines/AESNativeCBC.Java.

This issue affects Bouncy Castle for Java FIPS: 2.1.0; Bouncy Castle for Java LTS: from 2.73.0 through 2.73.7.

## References
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902025%E2%80%909341
- https://repo1.maven.org/maven2/org/bouncycastle
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/9xxx/CVE-2025-9341.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-9341
- https://github.com/bcgit/bc-lts-java
- ssh://bcgit@git.bouncycastle.org:bc-fips-2.1.X-java.git
