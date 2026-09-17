# [M] Garbage collection issue in BC-FJA in Java 13 and later

## Summary
Severity: Medium
Advisory: GHSA-68m8-v89j-7j2p
CVE: CVE-2022-45146
CWE: CWE-416
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-68m8-v89j-7j2p
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bc-fips` — affected >=0 <1.0.2.4

## Details
An issue was discovered in the FIPS Java API of Bouncy Castle BC-FJA before 1.0.2.4. Changes to the JVM garbage collector in Java 13 and later trigger an issue in the BC-FJA FIPS modules where it is possible for temporary keys used by the module to be zeroed out while still in use by the module, resulting in errors or potential information loss. 

NOTE: FIPS compliant users are unaffected because the FIPS certification is only for Java 7, 8, and 11.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45146
- https://github.com/bcgit/bc-java/wiki/CVE-2022-45146
- https://mvnrepository.com/artifact/org.bouncycastle/bc-fips
- https://www.bouncycastle.org/latest_releases.html
