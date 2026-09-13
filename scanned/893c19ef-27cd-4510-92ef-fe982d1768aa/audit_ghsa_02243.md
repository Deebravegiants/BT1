# [M] Timing based private key exposure in Bouncy Castle

## Summary
Severity: Medium
Advisory: GHSA-6xx3-rg99-gc3p
CVE: CVE-2020-15522
CWE: CWE-203, CWE-362
Ecosystem: Maven, NuGet
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-13
Source: https://github.com/advisories/GHSA-6xx3-rg99-gc3p
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bc-fips` — affected >=0 <1.0.2.1
- Maven: `org.bouncycastle:bcprov-ext-jdk15on` — affected >=0 <1.66
- Maven: `org.bouncycastle:bcprov-ext-jdk16` — affected >=0 <1.66
- Maven: `org.bouncycastle:bcprov-jdk14` — affected >=0 <1.66
- Maven: `org.bouncycastle:bcprov-jdk15` — affected >=0 <1.66
- Maven: `org.bouncycastle:bcprov-jdk15on` — affected >=0 <1.66
- Maven: `org.bouncycastle:bcprov-jdk15to18` — affected >=0 <1.66
- Maven: `org.bouncycastle:bcprov-jdk16` — affected >=0 <1.66
- NuGet: `BouncyCastle` — affected >=0 <1.8.7

## Details
Bouncy Castle BC Java before 1.66, BC C# .NET before 1.8.7, BC-FJA before 1.0.2.1, BC before 1.66, BC-FNA before 1.0.1.1 have a timing issue within the EC math library that can expose information about the private key when an attacker is able to observe timing information for the generation of multiple deterministic ECDSA signatures.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15522
- https://github.com/bcgit/bc-csharp/wiki/CVE-2020-15522
- https://github.com/bcgit/bc-java/wiki/CVE-2020-15522
- https://security.netapp.com/advisory/ntap-20210622-0007
- https://www.bouncycastle.org/releasenotes.html
