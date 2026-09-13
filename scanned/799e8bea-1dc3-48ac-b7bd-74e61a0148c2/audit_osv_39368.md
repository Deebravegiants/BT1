# [M] LinkAce: IDOR in Update Policies Allows Any Authenticated User to Overwrite Other Users' Links, Lists, Tags, and Notes

## Summary
Severity: Medium
Advisory: CVE-2026-45342
Aliases: GHSA-cj8f-h888-m57m
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-45342
Type: osv

## Details
LinkAce is a self-hosted archive to collect website links. Prior to 2.5.6, LinkAce contains an Insecure Direct Object Reference vulnerability in the authorization policy layer that allows any authenticated user to modify resources owned by other users. The affected resource types are links, lists, tags, and notes. Both the web UI and the REST API are vulnerable. The root cause is in the update() methods of all four model policies: LinkPolicy, LinkListPolicy, TagPolicy, and NotePolicy. Each delegates to an access-check method (e.g., userCanAccessLink()) that returns true for any resource with non-private visibility, regardless of who owns it. This means any registered user can edit any public or internal resource across the entire instance. The delete() methods in the same policy files correctly require ownership via $link->user->is($user), which confirms that update was intended to be owner-only. The same flaw exists in the API layer through AuthorizesUserApiActions::userCanUpdateModel(), which mirrors the broken visibility-only check instead of the ownership check used by userCanDeleteModel(). Bulk edit operations via BulkEditController are also affected. This vulnerability is fixed in 2.5.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45342.json
- https://github.com/Kovah/LinkAce/security/advisories/GHSA-cj8f-h888-m57m
- https://nvd.nist.gov/vuln/detail/CVE-2026-45342
