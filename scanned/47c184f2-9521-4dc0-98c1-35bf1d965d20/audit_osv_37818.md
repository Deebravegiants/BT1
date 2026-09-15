# [M] Authenticated users can read hidden forum posts through `/forum/get_quotes`

## Summary
Severity: Medium
Advisory: CVE-2026-33398
Aliases: GHSA-2r6x-cv4f-h8fx
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-02
Source: https://osv.dev/vulnerability/CVE-2026-33398
Type: osv

## Details
NamelessMC is website software for Minecraft servers. In version 2.2.4, `modules/Forum/pages/forum/get_quotes.php` only checks whether the caller is logged in, then reads a post by attacker-controlled `post` ID and returns its content. The backend helper in `modules/Forum/classes/Forum.php` does not enforce forum or topic ACLs. In contrast, the normal topic page in `modules/Forum/pages/forum/view_topic.php` enforces forum visibility and `view_other_topics`. Any low-privileged authenticated user can enumerate post IDs and read content from hidden, private, or staff-only forums. Version 2.2.5 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33398.json
- https://github.com/NamelessMC/Nameless/security/advisories/GHSA-2r6x-cv4f-h8fx
- https://nvd.nist.gov/vuln/detail/CVE-2026-33398
