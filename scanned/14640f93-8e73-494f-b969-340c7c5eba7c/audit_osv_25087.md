# [M] Reaction metadata exposed in private topics in Discourse-reactions

## Summary
Severity: Medium
Advisory: CVE-2023-30611
Aliases: GHSA-4cgc-c7vh-94g6
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2023-04-19
Source: https://osv.dev/vulnerability/CVE-2023-30611
Type: osv

## Details
Discourse-reactions is a plugin that allows user to add their reactions to the post in the Discourse messaging platform. In affected versions data about what reactions were performed on a post in a private topic could be leaked. This issue has been addressed in version 0.3. Users are advised to upgrade. Users unable to upgrade should disable the discourse-reactions plugin to fully mitigate the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30611.json
- https://github.com/discourse/discourse-reactions/security/advisories/GHSA-4cgc-c7vh-94g6
- https://nvd.nist.gov/vuln/detail/CVE-2023-30611
- https://github.com/discourse/discourse-reactions/commit/01aca15b2774c088f3673118e92e9469f37d2fb6
