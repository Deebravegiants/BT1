# [M] Path Traversal in Spring-integration-zip

## Summary
Severity: Medium
Advisory: GHSA-vw83-h3mq-3qwj
CVE: CVE-2021-22114
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-vw83-h3mq-3qwj
Type: github-advisory

## Affected
- Maven: `org.springframework.integration:spring-integration-zip` — affected >=0 <1.0.4

## Details
Addresses partial fix in CVE-2018-1263. Spring-integration-zip, versions prior to 1.0.4, exposes an arbitrary file write vulnerability, that can be achieved using a specially crafted zip archive (affects other archives as well, bzip2, tar, xz, war, cpio, 7z), that holds path traversal filenames. So when the filename gets concatenated to the target extraction directory, the final path ends up outside of the target folder.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22114
- https://tanzu.vmware.com/security/cve-2021-22114
