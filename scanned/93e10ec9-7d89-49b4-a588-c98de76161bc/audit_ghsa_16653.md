# [M] Bouncy Castle crafted signature and public key can be used to trigger an infinite loop

## Summary
Severity: Medium
Advisory: GHSA-m44j-cfrm-g8qc
CVE: CVE-2024-30172
CWE: CWE-835
Ecosystem: Maven, NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-m44j-cfrm-g8qc
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcprov-jdk18on` — affected >=1.73 <1.78
- Maven: `org.bouncycastle:bcprov-jdk15to18` — affected >=1.73 <1.78
- Maven: `org.bouncycastle:bcprov-jdk14` — affected >=1.73 <1.78
- Maven: `org.bouncycastle:bctls-jdk18on` — affected >=1.73 <1.78
- Maven: `org.bouncycastle:bctls-jdk14` — affected >=1.73 <1.78
- Maven: `org.bouncycastle:bctls-jdk15to18` — affected >=1.73 <1.78
- NuGet: `BouncyCastle` — affected >=0
- NuGet: `BouncyCastle.Cryptography` — affected >=0 <2.3.1

## Details
An issue was discovered in Bouncy Castle Java Cryptography APIs starting in 1.73 and before 1.78. An Ed25519 verification code infinite loop can occur via a crafted signature and public key.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-30172
- https://github.com/bcgit/bc-java/commit/1b9fd9b545e691bfb3941a9f6a797660c8860f02
- https://github.com/bcgit/bc-java/commit/9c165791b68a204678b48ec11e4e579754c2ea49
- https://github.com/bcgit/bc-java/commit/ebe1c75579170072dc59b8dee2b55ce31663178f
- https://github.com/bcgit/bc-csharp/wiki/CVE%E2%80%902024%E2%80%9030172
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902024%E2%80%9030172
- https://security.netapp.com/advisory/ntap-20240614-0007
- https://www.bouncycastle.org/latest_releases.html
