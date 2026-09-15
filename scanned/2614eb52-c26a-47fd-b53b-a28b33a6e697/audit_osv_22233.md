# [H] Improper write access check in Requarks/wiki

## Summary
Severity: High
Advisory: CVE-2022-23654
Aliases: GHSA-3cv9-795v-6j7j
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-02-22
Source: https://osv.dev/vulnerability/CVE-2022-23654
Type: osv

## Details
Wiki.js is a wiki app built on Node.js. In affected versions an authenticated user with write access on a restricted set of paths can update a page outside the allowed paths by specifying a different target page ID while keeping the path intact. The access control incorrectly check the path access against the user-provided values instead of the actual path associated to the page ID. Commit https://github.com/Requarks/wiki/commit/411802ec2f654bb5ed1126c307575b81e2361c6b fixes this vulnerability by checking access control on the path associated with the page ID instead of the user-provided value. When the path is different than the current value, a second access control check is then performed on the user-provided path before the move operation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23654.json
- https://github.com/Requarks/wiki/security/advisories/GHSA-3cv9-795v-6j7j
- https://nvd.nist.gov/vuln/detail/CVE-2022-23654
- https://github.com/Requarks/wiki/commit/411802ec2f654bb5ed1126c307575b81e2361c6b
