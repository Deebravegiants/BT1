# [H] Discourse BBCode plugin vulnerable to arbitrary CSS injection

## Summary
Severity: High
Advisory: CVE-2022-46162
Aliases: GHSA-8c87-xpqv-c7mp
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-30
Source: https://osv.dev/vulnerability/CVE-2022-46162
Type: osv

## Details
discourse-bbcode is the official BBCode plugin for Discourse. Prior to commit 91478f5, CSS injection can occur when rendering content generated with the discourse-bccode plugin. This vulnerability only affects sites which have the discourse-bbcode plugin installed and enabled. This issue is patched in commit 91478f5. As a workaround, ensure that the Content Security Policy is enabled and monitor any posts that contain bbcode.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/46xxx/CVE-2022-46162.json
- https://github.com/discourse/discourse-bbcode/security/advisories/GHSA-8c87-xpqv-c7mp
- https://nvd.nist.gov/vuln/detail/CVE-2022-46162
- https://github.com/discourse/discourse-bbcode/commit/91478f5cfecdcc43cf85b997168a8ecfd0f8df90
