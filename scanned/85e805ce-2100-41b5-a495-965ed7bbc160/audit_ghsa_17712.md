# [M] Directus allows privilege escalation using Share feature

## Summary
Severity: Medium
Advisory: GHSA-pmf4-v838-29hg
CVE: CVE-2025-24353
CWE: CWE-269
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2025-01-23
Source: https://github.com/advisories/GHSA-pmf4-v838-29hg
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <11.2.0
- npm: `@directus/app` — affected >=0 <13.3.1

## Details
### Summary
When sharing an item, user can specify an arbitrary role. It allows user to use a higher-privileged role to see fields that otherwise the user should not be able to see.

### Details
Specifying `role` on share should be available only for admins. The current flow has a security flaw.

Each other role should allow to share only in the context of the same role. As there is no role hierarchy in Directus, it is impossible to tell which role is _higher_ or _lower_, so only admins should be able to specify the role for share.

Optionally, instead of specifying a role, shareer* should be able to specify which fields (limited to fields shareer sees) are available on shared item. Similarily to import.

*_shareer_ - a person that creates a share link to item

### PoC
1. Create a collection with a secret field. 
2. Create role A that sees the secret field
3. Create role B that does not see the secret field, but can use share feature.
4. Create item with secret field filled. 
5. Use account with role B to share the object as role A and gain unauthorized access to secret value.

Here's video example: https://www.youtube.com/watch?v=DbV4IxbWzN4
I had to upload it to YouTube, because GitHub allows only 10MB videos.

### Impact
Impacted are instances that use the share feature and have specific roles hierarchy and fields that are not visible for certain roles.

## References
- https://github.com/directus/directus/security/advisories/GHSA-pmf4-v838-29hg
- https://nvd.nist.gov/vuln/detail/CVE-2025-24353
- https://github.com/directus/directus/pull/23716
- https://github.com/directus/directus/commit/e288a43a79613dada905da683f4919c6965ac804
- https://github.com/directus/directus
- https://github.com/directus/directus/releases/tag/v11.2.0
- https://www.youtube.com/watch?v=DbV4IxbWzN4
