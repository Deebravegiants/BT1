# [M] CVE-2021-41140

## Summary
Severity: Medium
Advisory: CVE-2021-41140
Aliases: GHSA-9358-hwg5-jrmh
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-10-19
Source: https://osv.dev/vulnerability/CVE-2021-41140
Type: osv

## Details
Discourse-reactions is a plugin for the Discourse platform that allows user to add their reactions to the post. In affected versions reactions given by user to secure topics and private messages are visible. This issue is patched in version 0.2 of discourse-reaction. Users who are unable to update are advised to disable the Discourse-reactions plugin in admin panel.

## References
- https://github.com/discourse/discourse-reactions/security/advisories/GHSA-9358-hwg5-jrmh
- https://github.com/discourse/discourse-reactions/commit/213d90b82fd15c4186ebc290fee18817d9727d0d
