# [M] SillyTavern: Path Traversal allows file existence oracle

## Summary
Severity: Medium
Advisory: GHSA-525j-2hrj-m8fp
CVE: CVE-2026-34523
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-525j-2hrj-m8fp
Type: github-advisory

## Affected
- npm: `sillytavern` — affected >=0 <1.17.0

## Details
### Summary

A path traversal vulnerability in the static file route handler allows any unauthenticated user to determine whether files exist anywhere on the server's filesystem. By sending percent-encoded `../` sequences (`%2E%2E%2F`) in requests to static file routes, an attacker can check for the existence of files (404 if it doesn't exist, 403 means it exists).

### Details

The vulnerability is in `createRouteHandler` (`src/users.js:947–963`), which backs all user-data static file routes:

```javascript
function createRouteHandler(directoryFn) {
    return async (req, res) => {
        const directory = directoryFn(req);
        const filePath = decodeURIComponent(req.params[0]);
        const exists = fs.existsSync(path.join(directory, filePath)); // no boundary check here
        if (!exists) {
            return res.sendStatus(404);
        }
        return res.sendFile(filePath, { root: directory });
    };
}
```

`req.params[0]` contains the raw (percent-encoded) wildcard from the URL. After `decodeURIComponent`, a request path like `/characters/%2E%2E%2F%2E%2E%2FUsers/kirakira` decodes to `../../Users/kirakira`, and `path.join` resolves it outside the intended directory. `res.sendFile` correctly blocks the file from being served (the `send` module's root check returns 403), but `fs.existsSync` had already run, and the 403/404 distinction reveals the result.

Affected routes (they all use the same handler, so they're all affected):

- `/characters/*`
- `/user/files/*`
- `/assets/*`
- `/user/images/*`
- `/backgrounds/*`
- `/User%20Avatars/*`

### PoC

```bash
curl -o /dev/null -s -w "%{http_code}\n" "http://localhost:8000/characters/%2E%2E%2F%2E%2E%2F%2E%2E%2F%2E%2E%2F%2E%2E%2F%2E%2E%2F%2E%2E%2FUsers/kirakira/something"
```

### Impact

While file contents cannot be read (the `send` module blocks actual delivery), anyone who can reach the SillyTavern HTTP port can check the existence of files on the host filesystem.

### Resolution

The issue was addressed in version 1.17.0.

## References
- https://github.com/SillyTavern/SillyTavern/security/advisories/GHSA-525j-2hrj-m8fp
- https://nvd.nist.gov/vuln/detail/CVE-2026-34523
- https://github.com/SillyTavern/SillyTavern
- https://github.com/SillyTavern/SillyTavern/releases/tag/1.17.0
