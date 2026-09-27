# [C] XML External Entity (XXE) vulnerability in Square Retrofit

## Summary
Severity: Critical
Advisory: GHSA-j379-9jr9-w5cq
CVE: CVE-2018-1000844
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2018-12-21
Source: https://github.com/advisories/GHSA-j379-9jr9-w5cq
Type: github-advisory

## Affected
- Maven: `com.squareup.retrofit2:retrofit` — affected >=2.0.0 <2.5.0

## Details
Square Open Source Retrofit versions prior to commit 4a693c5aeeef2be6c7ecf80e7b5ec79f6ab59437 contain a XML External Entity (XXE) vulnerability in JAXB. An attacker could use this to remotely read files from the file system or to perform SSRF. This vulnerability appears to have been fixed in commit 4a693c5aeeef2be6c7ecf80e7b5ec79f6ab59437.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000844
- https://github.com/square/retrofit/pull/2735
- https://github.com/advisories/GHSA-j379-9jr9-w5cq
- https://github.com/square/retrofit
