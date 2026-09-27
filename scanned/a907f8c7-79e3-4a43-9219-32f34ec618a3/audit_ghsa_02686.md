# [M] Member account takeover

## Summary
Severity: Medium
Advisory: GHSA-65p7-pjj8-ggmr
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-09-23
Source: https://github.com/advisories/GHSA-65p7-pjj8-ggmr
Type: github-advisory

## Affected
- npm: `ghost` — affected >=3.18.0 <3.42.6
- npm: `ghost` — affected >=4.0.0 <4.15.1

## Details
### Impact

An error in the implementation of the member email change functionality allows unauthenticated users to change the email address of arbitrary member accounts to one they control by crafting a request to the relevant API endpoint, and validating the new address via magic link sent to the new email address.

Ghost(Pro) has already been patched. Self-hosters are impacted if running Ghost a version between 3.18.0 and 4.15.0 with members functionality enabled.

### Patches

Fixed in 4.15.1, all 4.x sites should upgrade as soon as possible.
Fixed in 3.42.6, all 3.x sites should upgrade as soon as possible.

### Workarounds

The patch in 4.15.1 and 3.42.6 adds a new authenticated endpoint for updating member email addresses. Updating Ghost is the quickest complete solution.

As a workaround, if for any reason you cannot update your Ghost instance, you can block the `POST /members/api/send-magic-link/` endpoint, which will also disable member login and signup for your site.

### For more information

If you have any questions or comments about this advisory:
* Email us at [security@ghost.org](mailto:security@ghost.org)

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-65p7-pjj8-ggmr
- https://github.com/TryGhost/Ghost
