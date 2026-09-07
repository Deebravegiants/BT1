# [M] Bouncy Castle Vulnerable to Uncontrolled Resource Consumption

## Summary
Severity: Medium
Advisory: GHSA-jv6h-4262-q663
CVE: CVE-2025-12194
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:P/AU:N/R:U/V:C/RE:M/U:Amber (CVSS_V4)
Published: 2025-10-25
Source: https://github.com/advisories/GHSA-jv6h-4262-q663
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bc-fips` — affected >=2.1.0 <2.1.2
- Maven: `org.bouncycastle:bcprov-debug-lts8on` — affected >=2.73.0 <2.73.8

## Details
Uncontrolled Resource Consumption vulnerability in Legion of the Bouncy Castle Inc. Bouncy Castle for Java FIPS bc-fips on All (API modules), Legion of the Bouncy Castle Inc. Bouncy Castle for Java LTS bcprov-lts8on on All (API modules) allows Excessive Allocation. This vulnerability is associated with program files core/src/main/jdk1.9/org/bouncycastle/crypto/fips/AESNativeCFB.Java, core/src/main/jdk1.9/org/bouncycastle/crypto/fips/AESNativeGCM.Java, core/src/main/jdk1.9/org/bouncycastle/crypto/fips/SHA256NativeDigest.Java, core/src/main/jdk1.9/org/bouncycastle/crypto/fips/AESNativeEngine.Java, core/src/main/jdk1.9/org/bouncycastle/crypto/fips/AESNativeCBC.Java, core/src/main/jdk1.9/org/bouncycastle/crypto/fips/AESNativeCTR.Java, core/src/main/jdk1.9/org/bouncycastle/crypto/engines/AESNativeCFB.Java, core/src/main/jdk1.9/org/bouncycastle/crypto/engines/AESNativeGCM.Java, core/src/main/jdk1.9/org/bouncycastle/crypto/engines/AESNativeEngine.Java, core/src/main/jdk1.9/org/bouncycastle/crypto/engines/AESNativeCBC.Java, core/src/main/jdk1.9/org/bouncycastle/crypto/engines/AESNativeGCMSIV.Java, core/src/main/jdk1.9/org/bouncycastle/crypto/engines/AESNativeCCM.Java, core/src/main/jdk1.9/org/bouncycastle/crypto/engines/AESNativeCTR.Java, core/src/main/jdk1.9/org/bouncycastle/crypto/digests/SHA256NativeDigest.Java, core/src/main/jdk1.9/org/bouncycastle/crypto/digests/SHA224NativeDigest.Java, core/src/main/jdk1.9/org/bouncycastle/crypto/digests/SHA3NativeDigest.Java, core/src/main/jdk1.9/org/bouncycastle/crypto/digests/SHAKENativeDigest.Java, core/src/main/jdk1.9/org/bouncycastle/crypto/digests/SHA512NativeDigest.Java, core/src/main/jdk1.9/org/bouncycastle/crypto/digests/SHA384NativeDigest.Java.

This issue affects Bouncy Castle for Java FIPS: from 2.1.0 through 2.1.1; Bouncy Castle for Java LTS: from 2.73.0 through 2.73.7.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12194
- https://github.com/bcgit/bc-lts-java/commit/2c9be6c64152ce48c6afc784c042a514be71ec71
- https://github.com/bcgit/bc-lts-java/commit/f2776feac0c30230f7a5ac34eb24f5019caf0324
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902025%E2%80%9012194
- https://github.com/bcgit/bc-lts-java
