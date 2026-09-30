# [M] Unauthorized Access to User Chat History in gaizhenbiao/chuanhuchatgpt

## Summary
Severity: Medium
Advisory: CVE-2024-8143
Aliases: PYSEC-2024-113
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-8143
Type: osv

## Details
In the latest version (20240628) of gaizhenbiao/chuanhuchatgpt, an issue exists in the /file endpoint that allows authenticated users to access the chat history of other users. When a user logs in, a directory is created in the history folder with the user's name. By manipulating the /file endpoint, an authenticated user can enumerate and access files in other users' directories, leading to unauthorized access to private chat histories. This vulnerability can be exploited to read any user's private chat history.

## References
- https://huntr.com/bounties/71c5ea4b-524a-4173-8fd4-2fbabd69502e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8143.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-8143
- https://github.com/gaizhenbiao/chuanhuchatgpt/commit/ccc7479ace5c9e1a1d9f4daf2e794ffd3865fc2b
