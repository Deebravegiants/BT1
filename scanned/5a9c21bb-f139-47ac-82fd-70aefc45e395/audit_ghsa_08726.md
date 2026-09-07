# [M] Bouncy Castle LTS native GCM chunking can cause bad-tag exception on decryption

## Summary
Severity: Medium
Advisory: GHSA-mx76-r943-rf8g
CVE: CVE-2026-8149
CWE: CWE-1068, CWE-354
Ecosystem: Maven
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-mx76-r943-rf8g
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcprov-lts8on` — affected >=2.73.0 <2.73.11

## Details
In Bouncy Castle LTS for Java, the AES/GCM native implementation used on Intel CPUs with AES PAA instruction sets (AVX / VAES / VAESF variants) can intermittently produce an incorrect authentication tag verification result during decryption when the ciphertext is fed in via a mix of `update()` calls followed by `doFinal()`. It is possible to work around it by either using `doFinal()` only (as the BCJSSE does) or by configuring the module to run in pure Java mode, by setting the system property "org.bouncycastle.native.cpu_variant" to java.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8149
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902026%E2%80%908149
