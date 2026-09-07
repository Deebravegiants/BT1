# [M] Parse Server: File metadata endpoint bypasses `beforeFind` / `afterFind` trigger authorization

## Summary
Severity: Medium
Advisory: GHSA-hwx8-q9cg-mqmc
CVE: CVE-2026-30850
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-hwx8-q9cg-mqmc
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <8.6.9
- npm: `parse-server` — affected >=9.0.0-alpha.1 <9.5.0-alpha.9

## Details
### Impact

The file metadata endpoint (GET `/files/:appId/metadata/:filename`) does not enforce `beforeFind` / `afterFind` file triggers. When these triggers are used as access-control gates, the metadata endpoint bypasses them entirely, allowing unauthorized access to file metadata.

This affects any deployment that relies on `Parse.Cloud.beforeFind(Parse.File, ...)` to restrict file access. Only file metadata (user-defined key-value pairs set via addMetadata) is exposed; file content remains protected.

### Patches

The metadata handler now runs `beforeFind` and `afterFind` triggers and returns HTTP 403 when a trigger denies access.

### Workarounds

Disable the `metadata` endpoint by overriding the route with a middleware that rejects all requests:

```js
// Add before mounting Parse Server
app.get('/parse/files/:appId/metadata/:filename', (req, res) => {
  res.status(403).json({ error: 'Forbidden' });
});
```

Adjust the path prefix (`/parse`) to match your mountPath.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-hwx8-q9cg-mqmc
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.0-alpha.9
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.9

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-hwx8-q9cg-mqmc
- https://nvd.nist.gov/vuln/detail/CVE-2026-30850
- https://github.com/parse-community/parse-server
