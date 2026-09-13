# [M] User object created with invalid provider data in GoTrue

## Summary
Severity: Medium
Advisory: GHSA-wpfr-6297-9v57
Ecosystem: Go
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-wpfr-6297-9v57
Type: github-advisory

## Affected
- Go: `github.com/netlify/gotrue` — affected >=0 <1.0.1

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

Under certain circumstances a valid user object would have been created with invalid provider metadata.

This vulnerability affects everyone running an instance of GoTrue as a service. We advise you to update especially if you are using the provider metadata from the user object to secure other resources.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

A patch is available with the release of version [1.0.1 on Github](https://github.com/netlify/gotrue/releases/tag/v1.0.1).

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

If you don't rely on the provider metadata in the user object, you might not be affected. We still strongly recommend upgrading.

### References
_Are there any links users can visit to find out more?_

This problem was initially found and reported by the team at Supabase: https://github.com/supabase/gotrue/security/advisories/GHSA-5hvv-9cqv-894r. We want to thank them for the cooperation around this report.

In contrast to their advisory, we decided to set the severity to "Moderate" since the provider metadata is not an inherent security feature of this GoTrue codebase or the Netlify ecosystem.

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@netlify.com](mailto:security@netlify.com)

## References
- https://github.com/netlify/gotrue/security/advisories/GHSA-wpfr-6297-9v57
- https://github.com/netlify/gotrue/pull/313
- https://github.com/netlify/gotrue/commit/4d8a3b39fe485a5f83c70617d594be01130c5b83
- https://github.com/netlify/gotrue
- https://github.com/netlify/gotrue/releases/tag/v1.0.1
