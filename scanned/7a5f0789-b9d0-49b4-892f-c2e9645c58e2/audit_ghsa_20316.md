# [M] Ghost vulnerable to remote code execution in locale setting change

## Summary
Severity: Medium
Advisory: GHSA-7v28-g2pq-ggg8
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-7v28-g2pq-ggg8
Type: github-advisory

## Affected
- npm: `ghost` — affected >=0 <4.48.2
- npm: `ghost` — affected >=5.0.0 <5.2.3

## Details
### Impact

A [vulnerability](https://www.cve.org/CVERecord?id=CVE-2022-24785) in an upstream library means an authenticated attacker can abuse locale input to execute arbitrary commands from a file that has previously been uploaded using the file upload functionality in the post editor.

### Patches

Fixed in 5.2.3, all 5.x sites should update as soon as possible.
Fixed in 4.48.2, all 4.x sites should update as soon as possible.

### Workarounds

Patched versions of Ghost add validation to the locale input to prevent execution of arbitrary files. Updating Ghost is the quickest complete solution.

As a workaround, if for any reason you cannot update your Ghost instance, you can block the `POST /ghost/api/admin/settings/` endpoint, which will also disable updating settings for your site.

### For more information

If you have any questions or comments about this advisory:
* Email us at [security@ghost.org](mailto:security@ghost.org)

### Credits

* devx00 - https://twitter.com/devx00

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-7v28-g2pq-ggg8
- https://github.com/TryGhost/Ghost
