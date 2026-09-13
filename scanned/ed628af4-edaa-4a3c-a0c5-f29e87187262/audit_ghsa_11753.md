# [H] @tinacms/graphql has Path Traversal that leads to overwrite of arbitrary files

## Summary
Severity: High
Advisory: GHSA-v9p7-gf3q-h779
CVE: CVE-2026-33949
CWE: CWE-22, CWE-73
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-v9p7-gf3q-h779
Type: github-advisory

## Affected
- npm: `@tinacms/graphql` — affected >=0 <2.2.2

## Details
### Summary
A Path Traversal vulnerability in `@tinacms/graphql` allows unauthenticated users to write and overwrite arbitrary files within the project root. This is achieved by manipulating the `relativePath` parameter in GraphQL mutations. The impact includes the ability to replace critical server configuration files and potentially execute arbitrary commands by sabotaging build scripts.

### Details
The vulnerability exists in the path validation logic within `@tinacms/graphql`. Specifically, the regex-based validation in `getValidatedPath` fails to recognize backslashes (`\`) as directory separators on non-Windows platforms (Mac/Linux). An attacker can provide a path like `x\..\..\..\package.json`, which bypasses the validation check but is subsequently treated as a traversal path during file I/O operations by the underlying `fs` modules and path normalization utilities.

Incriminated code areas:
- [packages/@tinacms/graphql/src/database/bridge/filesystem.ts](tinacms/packages/@tinacms/graphql/src/database/bridge/filesystem.ts): [assertWithinBase](tinacms/graphql/src/database/bridge/filesystem.ts#7-35) function.
- [packages/@tinacms/graphql/src/resolver/index.ts](tinacms/packages/@tinacms/graphql/src/resolver/index.ts): `getValidatedPath` function.

### PoC
1. Start the TinaCMS development server.
2. Send a malicious GraphQL mutation to overwrite a project file (e.g., [package.json](tinacms/examples/tina-self-hosted-demo/package.json)):

```bash
curl -X POST http://localhost:4001/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { updateDocument(collection: \"global\", relativePath: \"x\\\\..\\\\..\\\\..\\\\package.json\", params: { global: { header: { name: \"OVERWRITTEN\" } } }) { __typename } }"}'
```

3. Observe that the root [package.json](tinacms/examples/tina-self-hosted-demo/package.json) has been replaced with the provided payload.

<img width="1424" height="516" alt="2026-03-15_12-24-05 PM" src="https://github.com/user-attachments/assets/9fdf94ce-2183-4a24-9cd9-48f21deb9768" />

<img width="1387" height="774" alt="2026-03-15_12-27-33 PM" src="https://github.com/user-attachments/assets/676f083b-f934-4cf2-978b-bb2fabee0216" />

### Impact
This is an **Arbitrary File Write** vulnerability. Any unauthenticated user with network access to the GraphQL API can:
- Overwrite critical server configuration files (e.g., [package.json](tinacms/examples/tina-self-hosted-demo/package.json), [tsconfig.json](tinacms/examples/tina-self-hosted-demo/tsconfig.json)).
- Host malicious scripts in the `public/` directory for client-side attacks.
- Perform **Arbitrary Code Execution** by modifying build scripts or server-side logic files that are subsequently executed by the environment.



**Weaknesses:**
- **CWE-22**: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')
- **CWE-73**: External Control of File Name or Path

## References
- https://github.com/tinacms/tinacms/security/advisories/GHSA-v9p7-gf3q-h779
- https://nvd.nist.gov/vuln/detail/CVE-2026-33949
- https://github.com/tinacms/tinacms
