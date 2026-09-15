# [M] CVE-2020-15124

## Summary
Severity: Medium
Advisory: CVE-2020-15124
Aliases: GHSA-7gwq-xqw3-cr63
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-07-22
Source: https://osv.dev/vulnerability/CVE-2020-15124
Type: osv

## Details
In Goobi Viewer Core before version 4.8.3, a path traversal vulnerability allows for remote attackers to access files on the server via the application. This is limited to files accessible to the application server user, eg. tomcat, but can potentially lead to the disclosure of sensitive information. The vulnerability has been fixed in version 4.8.3

## References
- https://github.com/intranda/goobi-viewer-core/security/advisories/GHSA-7gwq-xqw3-cr63
- https://github.com/intranda/goobi-viewer-core/commit/44ceb8e2e7e888391e8a941127171d6366770df3
