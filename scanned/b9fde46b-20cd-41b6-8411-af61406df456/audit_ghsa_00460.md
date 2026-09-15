# [M] Path traversal in org.springframework.integration:spring-integration-zip

## Summary
Severity: Medium
Advisory: GHSA-m9jm-rhrm-gcxj
CVE: CVE-2018-1261
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-10-18
Source: https://github.com/advisories/GHSA-m9jm-rhrm-gcxj
Type: github-advisory

## Affected
- Maven: `org.springframework.integration:spring-integration-zip` — affected >=0 <1.0.1

## Details
Spring-integration-zip versions prior to 1.0.1 exposes an arbitrary file write vulnerability, which can be achieved using a specially crafted zip archive (affects other archives as well, bzip2, tar, xz, war, cpio, 7z) that holds path traversal filenames. So when the filename gets concatenated to the target extraction directory, the final path ends up outside of the target folder.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1261
- https://github.com/spring-projects/spring-integration-extensions/commit/a5573eb232ff85199ff9bb28993df715d9a19a25
- https://github.com/advisories/GHSA-m9jm-rhrm-gcxj
- https://github.com/spring-projects/spring-integration-extensions
- https://pivotal.io/security/cve-2018-1261
- http://www.securityfocus.com/bid/104178
