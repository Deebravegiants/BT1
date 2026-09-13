# [C] ClipBucket V5 Playlist Cover File Upload to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2025-21624
Aliases: GHSA-98vm-2xqm-xrcc
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-07
Source: https://osv.dev/vulnerability/CVE-2025-21624
Type: osv

## Details
ClipBucket V5 provides open source video hosting with PHP. Prior to 5.5.1 - 239, a file upload vulnerability exists in the Manage Playlist functionality of the application, specifically surrounding the uploading of playlist cover images. Without proper checks, an attacker can upload a PHP script file instead of an image file, thus allowing a webshell or other malicious files to be stored and executed on the server. This attack vector exists in both the admin area and low-level user area. This vulnerability is fixed in 5.5.1 - 239.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21624.json
- https://github.com/MacWarrior/clipbucket-v5/security/advisories/GHSA-98vm-2xqm-xrcc
- https://nvd.nist.gov/vuln/detail/CVE-2025-21624
- https://github.com/MacWarrior/clipbucket-v5/commit/893bfb0f1236c4a59b5e2843ab8d27a1e491b12b
