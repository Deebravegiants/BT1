# [C] Quarkus does not terminate HTTP requests header context

## Summary
Severity: Critical
Advisory: GHSA-mwhw-6p27-4crc
CVE: CVE-2022-2466
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-01
Source: https://github.com/advisories/GHSA-mwhw-6p27-4crc
Type: github-advisory

## Affected
- Maven: `io.quarkus:quarkus-core-parent` — affected >=2.10.0 <2.10.4

## Details
Quarkus is a Cloud Native, (Linux) Container First framework for writing Java applications. It was found that Quarkus 2.10.x does not terminate HTTP requests header context which may lead to unpredictable behavior. This issue was fixed in version 2.10.4Final.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2466
- https://github.com/quarkusio/quarkus/issues/26748
- https://github.com/quarkusio/quarkus
- https://github.com/quarkusio/quarkus/releases/tag/2.10.4.Final
