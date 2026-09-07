# [C] FasterXML jackson-databind allows unauthenticated remote code execution 

## Summary
Severity: Critical
Advisory: GHSA-cggj-fvv3-cqwv
CVE: CVE-2018-7489
CWE: CWE-184, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-cggj-fvv3-cqwv
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.8.0 <2.8.11.1
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.9.0 <2.9.5
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.7.0 <2.7.9.3
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=0 <2.6.7.5

## Details
FasterXML jackson-databind before before 2.6.7.5, 2.7.x before 2.7.9.3, 2.8.x before 2.8.11.1, and 2.9.x before 2.9.5 allows unauthenticated remote code execution because of an incomplete fix for the CVE-2017-7525 deserialization flaw. This is exploitable by sending maliciously crafted JSON input to the readValue method of the ObjectMapper, bypassing a blacklist that is ineffective if the c3p0 libraries are available in the classpath.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7489
- https://github.com/FasterXML/jackson-databind/issues/1931
- https://github.com/FasterXML/jackson-databind/commit/e66c0a9d3c926ff1b63bf586c824ead1d02f2a3d
- https://github.com/FasterXML/jackson-databind/commit/ca2bfc86af82a1479112004b663ba74c760752e6
- https://github.com/FasterXML/jackson-databind/commit/c921f0935d5e41bf206e702d8077a275ba1a6efc
- https://github.com/FasterXML/jackson-databind/commit/6799f8f10cc78e9af6d443ed6982d00a13f2e7d2
- https://github.com/FasterXML/jackson-databind/commit/bc22f90eb7f896ace9567598a99cb1ff6e0f9d9d
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.debian.org/security/2018/dsa-4190
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03902en_us
- https://security.netapp.com/advisory/ntap-20180328-0001
- https://lists.apache.org/thread.html/r1d4a247329a8478073163567bbc8c8cb6b49c6bfc2bf58153a857af1@%3Ccommits.druid.apache.org%3E
- https://github.com/advisories/GHSA-cggj-fvv3-cqwv
- https://github.com/FasterXML/jackson-databind
- https://access.redhat.com/errata/RHSA-2019:3149
- https://access.redhat.com/errata/RHSA-2019:2858
- https://access.redhat.com/errata/RHSA-2018:2939
