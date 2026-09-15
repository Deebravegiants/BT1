# [H] Wikmd vulnerable to Local File Enumeration when accessing /list

## Summary
Severity: High
Advisory: CVE-2022-36081
Aliases: GHSA-w4cf-92x9-v8w2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-09-07
Source: https://osv.dev/vulnerability/CVE-2022-36081
Type: osv

## Details
Wikmd is a file based wiki that uses markdown. Prior to version 1.7.1, Wikmd is vulnerable to path traversal when accessing `/list/<path:folderpath>` and discloses lists of files located on the server including sensitive data. Version 1.7.1 fixes this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/36xxx/CVE-2022-36081.json
- https://github.com/Linbreux/wikmd/security/advisories/GHSA-w4cf-92x9-v8w2
- https://nvd.nist.gov/vuln/detail/CVE-2022-36081
- https://github.com/Linbreux/wikmd/commit/8d1f94ec86b5b6c3df8ef10051facfb511a78450
