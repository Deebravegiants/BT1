# [M] Uncaught Exception in zip4j

## Summary
Severity: Medium
Advisory: GHSA-q62h-jw38-24vh
CVE: CVE-2022-24615
CWE: CWE-248, CWE-755
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-25
Source: https://github.com/advisories/GHSA-q62h-jw38-24vh
Type: github-advisory

## Affected
- Maven: `net.lingala.zip4j:zip4j` — affected >=0 <2.10.0

## Details
zip4j up to 2.9.1 can throw various uncaught exceptions while parsing a specially crafted ZIP file, which could result in an application crash. This could be used to mount a denial of service attack against services that use zip4j library.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24615
- https://github.com/srikanth-lingala/zip4j/issues/377
- https://github.com/srikanth-lingala/zip4j/issues/418
- https://github.com/srikanth-lingala/zip4j
