# [H] Joplin Server Vulnerable to Path Traversal

## Summary
Severity: High
Advisory: CVE-2025-27409
Aliases: GHSA-5xv6-7jm3-fmg5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-04-30
Source: https://osv.dev/vulnerability/CVE-2025-27409
Type: osv

## Details
Joplin is a free, open source note taking and to-do application, which can handle a large number of notes organised into notebooks. Prior to version 3.3.3, path traversal is possible in Joplin Server if static file path starts with `css/pluginAssets` or `js/pluginAssets`. The `findLocalFile` function in the `default route` calls `localFileFromUrl` to check for special `pluginAssets` paths. If the function returns a path, the result is returned directly, without checking for path traversal. The vulnerability allows attackers to read files outside the intended directories. This issue has been patched in version 3.3.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27409.json
- https://github.com/laurent22/joplin/security/advisories/GHSA-5xv6-7jm3-fmg5
- https://nvd.nist.gov/vuln/detail/CVE-2025-27409
- https://github.com/laurent22/joplin/pull/11916
