# [M] Path traversal for local publishers in TechDocs backend

## Summary
Severity: Medium
Advisory: GHSA-4jqc-jvh2-pxg9
Ecosystem: npm
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-4jqc-jvh2-pxg9
Type: github-advisory

## Affected
- npm: `@backstage/plugin-techdocs-node` — affected >=0 <1.1.2
- npm: `@backstage/techdocs-common` — affected >=0 <0.11.16

## Details
### Impact
A malicious actor with the ability to register entities in the Software Catalog is able to write files to arbitrary paths on the techdocs backend host instance when `techdocs.publisher.type` is set to `local`.

This vulnerability is mitigated by the fact that the Software Catalog must be configured with non-standard field format validators and/or non-standard entity policies.

### Patches
Those affected are advised to upgrade to `@backstage/plugin-techdocs-node` version `1.1.2` or higher.

### Workarounds
If patching or upgrading is not possible, it would be sufficient to update any custom Catalog field format validators and/or custom entity policies to disallow entity names, kinds, and namespaces containing `..`

<!--
### References
todo: Link to blog post / published report.
-->

### For more information
If you have any questions or comments about this advisory:

- Open an issue in the [Backstage repository](https://github.com/backstage/backstage)
- Visit our chat, linked to in the [Backstage README](https://github.com/backstage/backstage)

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-4jqc-jvh2-pxg9
- https://github.com/backstage/backstage/commit/429c9f9daa5654dd1b996aa85f7264eb23a2e4fa
- https://github.com/backstage/backstage
