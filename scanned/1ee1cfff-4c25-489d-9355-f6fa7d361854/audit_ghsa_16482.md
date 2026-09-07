# [M] Bouncy Castle certificate parsing issues cause high CPU usage during parameter evaluation.

## Summary
Severity: Medium
Advisory: GHSA-8xfc-gm6g-vgpv
CVE: CVE-2024-29857
CWE: CWE-125, CWE-400
Ecosystem: Maven, NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-8xfc-gm6g-vgpv
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcprov-jdk18on` — affected >=0 <1.78
- Maven: `org.bouncycastle:bcprov-jdk15on` — affected >=0 <1.78
- Maven: `org.bouncycastle:bcprov-jdk15to18` — affected >=0 <1.78
- Maven: `org.bouncycastle:bcprov-jdk14` — affected >=0 <1.78
- Maven: `org.bouncycastle:bctls-jdk18on` — affected >=0 <1.78
- Maven: `org.bouncycastle:bctls-jdk14` — affected >=0 <1.78
- Maven: `org.bouncycastle:bctls-jdk15to18` — affected >=0 <1.78
- Maven: `org.bouncycastle:bc-fips` — affected >=0 <1.0.2.5
- NuGet: `BouncyCastle` — affected >=0
- NuGet: `BouncyCastle.Cryptography` — affected >=0 <2.3.1

## Details
An issue was discovered in ECCurve.java and ECCurve.cs in Bouncy Castle Java (BC Java) before 1.78, BC Java LTS before 2.73.6, BC-FJA before 1.0.2.5, and BC C# .Net before 2.3.1. Importing an EC certificate with crafted F2m parameters can lead to excessive CPU consumption during the evaluation of the curve parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29857
- https://github.com/bcgit/bc-csharp/commit/56daa6eac526f165416d17f661422d60de0dfd63
- https://github.com/bcgit/bc-java/commit/efc498ca4caa340ac2fe11f2efee06c1a294501f
- https://github.com/bcgit/bc-java/commit/fee80dd230e7fba132d03a34f1dd1d6aae0d0281
- https://github.com/bcgit/bc-csharp/wiki/CVE%E2%80%902024%E2%80%9029857
- https://github.com/bcgit/bc-java/wiki/CVE%E2%80%902024%E2%80%9029857
- https://security.netapp.com/advisory/ntap-20241206-0008
- https://www.bouncycastle.org/latest_releases.html
