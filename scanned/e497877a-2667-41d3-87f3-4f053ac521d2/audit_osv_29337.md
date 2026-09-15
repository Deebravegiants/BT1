# [C] Elektra vulnerable to remote code execution in universal search

## Summary
Severity: Critical
Advisory: CVE-2024-41961
Aliases: GHSA-6j2h-486h-487q
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:H/E:X/RL:O/RC:C)
Published: 2024-08-01
Source: https://osv.dev/vulnerability/CVE-2024-41961
Type: osv

## Details
Elektra is an opinionated Openstack Dashboard for Operators and Consumers of Openstack Services. A code injection vulnerability was found in the live search functionality of the Ruby on Rails based Elektra web application. An authenticated user can craft a search term containing Ruby code, which later flows into an `eval` sink which executes the code. Fixed in commit 8bce00be93b95a6512ff68fe86bf9554e486bc02.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41961.json
- https://github.com/sapcc/elektra/security/advisories/GHSA-6j2h-486h-487q
- https://nvd.nist.gov/vuln/detail/CVE-2024-41961
- https://github.com/sapcc/elektra/commit/49aea3b365082681558bf3bf7bf4a51766cfc44d
- https://github.com/sapcc/elektra/commit/8bce00be93b95a6512ff68fe86bf9554e486bc02
