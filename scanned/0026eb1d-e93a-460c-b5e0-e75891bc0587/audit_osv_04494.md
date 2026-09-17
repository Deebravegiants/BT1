# [M] Discourse has check revision visibility on posts endpoint

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-27454
Aliases: CVE-2026-27454, GHSA-fq69-f929-wp96
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-27454
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.3.0

## Details
Discourse is an open-source discussion platform. Prior to versions 2026.3.0, 2026.2.1, and 2026.1.2, requesting /posts/:id.json?version=X bypassed authorization checks on post revisions. The display_post method called post.revert_to directly without verifying whether the revision was hidden or if the user had permission to view edit history. This meant hidden revisions (intentionally concealed by staff) could be read by any user by simply enumerating version numbers. Starting in versions 2026.3.0, 2026.2.1, and 2026.1.2, Discourse looks up the PostRevision and call guardian.ensure_can_see! before reverting, consistent with how the /posts/:id/revisions/:revision endpoint already authorizes access. No known workarounds are available.

## References
- https://github.com/discourse/discourse/commit/8510fde30eb0d7f2dee822a95f6cf43b9ac943d0
- https://github.com/discourse/discourse/commit/c0eeb5892f5d61ad62b057f4d468333a6e9f28c3
- https://github.com/discourse/discourse/commit/c474fbd79d2bd231baafb4332970297d781f92ca
- https://github.com/discourse/discourse/security/advisories/GHSA-fq69-f929-wp96
- https://nvd.nist.gov/vuln/detail/CVE-2026-27454
