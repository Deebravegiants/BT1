# [M] Native ARM SHA3 / SHAKE `restoreFullState`  fails to detect size_t underflow in a crafted encoded state

## Summary
Severity: Medium
Advisory: CVE-2026-15997
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:N/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U/S:P/AU:N/R:A/V:D/RE:M/U:Amber)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-15997
Type: osv

## Details
Out-of-bounds write vulnerability in Legion of the Bouncy Castle Inc. BC-LTS bcprov-lts8on on ARM allows Overflow Buffers.

 This vulnerability is associated with program files https://github.Com/bcgit/bc-lts-java/blob/main/native_c/arm/sha/shake.C, https://github.Com/bcgit/bc-lts-java/blob/main/native_c/arm/sha/sha3.C.



This issue affects BC-LTS: from 2.73.0 before 2.73.12.1.



Issue is only applicable if application involved is accepting memoable SHA3 / SHAKE states from potentially untrusted sources.

## References
- https://github.com/bcgit/bc-lts-java/wiki/CVE-2026-15997
- https://www.bouncycastle.org/download/bouncy-castle-java-lts/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15997.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15997
- https://github.com/bcgit/bc-lts-java
