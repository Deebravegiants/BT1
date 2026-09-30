# [H] Outline's IDOR allows unauthorized viewing and seizing of private deleted drafts

## Summary
Severity: High
Advisory: CVE-2026-24901
Aliases: GHSA-gmr5-43f5-79f5
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-03-17
Source: https://osv.dev/vulnerability/CVE-2026-24901
Type: osv

## Details
Outline is a service that allows for collaborative documentation. Prior to 1.4.0, an Insecure Direct Object Reference (IDOR) vulnerability in the document restoration logic allows any team member to unauthorizedly restore, view, and seize ownership of deleted drafts belonging to other users, including administrators. By bypassing ownership validation during the restore process, an attacker can access sensitive private information and effectively lock the original owner out of their own content. Version 1.4.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24901.json
- https://github.com/outline/outline/security/advisories/GHSA-gmr5-43f5-79f5
- https://nvd.nist.gov/vuln/detail/CVE-2026-24901
