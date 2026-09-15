# [M] spring-integration-zip Arbitrary File Write

## Summary
Severity: Medium
Advisory: GHSA-87vg-5pgx-pggh
CVE: CVE-2018-1263
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-87vg-5pgx-pggh
Type: github-advisory

## Affected
- Maven: `org.springframework.integration:spring-integration-zip` — affected >=0 <1.0.2

## Details
Addresses partial fix in CVE-2018-1261. Pivotal spring-integration-zip, versions prior to 1.0.2, exposes an arbitrary file write vulnerability, that can be achieved using a specially crafted zip archive (affects other archives as well, bzip2, tar, xz, war, cpio, 7z), that holds path traversal filenames. So when the filename gets concatenated to the target extraction directory, the final path ends up outside of the target folder.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1263
- https://github.com/spring-projects/spring-integration-extensions/commit/d10f537283d90eabd28af57ac97f860a3913bf9b
- https://github.com/spring-projects/spring-integration
- https://pivotal.io/security/cve-2018-1263
- https://web.archive.org/web/20210125210559/https://www.securityfocus.com/bid/104179
