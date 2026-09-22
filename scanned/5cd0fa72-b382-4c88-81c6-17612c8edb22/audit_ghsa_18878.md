# [M] lsFusion Platform has a Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5jpg-2rj5-964c
CVE: CVE-2025-13261
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-11-17
Source: https://github.com/advisories/GHSA-5jpg-2rj5-964c
Type: github-advisory

## Affected
- Maven: `lsfusion.platform:web-client` — affected >=0

## Details
A vulnerability was found in lsfusion platform up to 6.1. Affected is the function DownloadFileRequestHandler of the file web-client/src/main/java/lsfusion/http/controller/file/DownloadFileRequestHandler.java. Performing manipulation of the argument Version results in path traversal. Remote exploitation of the attack is possible. The exploit has been made public and could be used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-13261
- https://github.com/lsfusion/platform/issues/1543
- https://github.com/lsfusion/platform/issues/1543#issue-3576922131
- https://github.com/lsfusion/platform
- https://vuldb.com/?ctiid.332596
- https://vuldb.com/?id.332596
- https://vuldb.com/?submit.689412
