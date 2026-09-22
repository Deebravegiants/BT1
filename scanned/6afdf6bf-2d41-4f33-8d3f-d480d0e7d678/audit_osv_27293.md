# [M] ML-KEM (Kyber) decapsulation leaks private key information through non-constant-time division in message decoding and ciphertext compression (KyberSlash)

## Summary
Severity: Medium
Advisory: CVE-2024-14041
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/U:Amber)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/CVE-2024-14041
Type: osv

## Details
In Bouncy Castle for Java from 1.73 to before 1.78, three ML-KEM (CRYSTALS-Kyber) routines divided secret-derived polynomial coefficients by the modulus q: Poly.toMsg, which decodes the decrypted message, and the ciphertext compression routines Poly.compressPoly and PolyVec.compressPolyVec. An attacker able to measure the timing of a large number of decapsulations performed with the same long-term private key can recover that key. These are the KyberSlash1 (Poly.toMsg) and KyberSlash2 (ciphertext compression) divisions. Compression performed during encapsulation operates on values that become the public ciphertext and is not affected.

## References
- https://www.bouncycastle.org/download/bouncy-castle-java/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/14xxx/CVE-2024-14041.json
- https://github.com/bcgit/bc-java/wiki/CVE-2024-14041
- https://nvd.nist.gov/vuln/detail/CVE-2024-14041
- https://github.com/bcgit/bc-java/commit/1590247178f2280defa36421475f015175dfbe9e
- https://github.com/bcgit/bc-java/commit/5adb2c5c5b462a332b01a012bea0784b40b904e5
- https://github.com/bcgit/bc-java
- https://kyberslash.cr.yp.to/
