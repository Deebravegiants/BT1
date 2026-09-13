# [H] Siyuan: Authenticated path traversal in /snippets/ static handler (serveSnippets) leaks conf/conf.json secrets and siyuan.db

## Summary
Severity: High
Advisory: GHSA-275h-v5h9-vr82
CVE: CVE-2026-59832
CWE: CWE-22, CWE-23
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-275h-v5h9-vr82
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260704035520-68cc0f537dfa

## Details
Reporter: Cavan Loughran, Celvex Group Inc.

Summary
-------
The /snippets/*filepath route handler serveSnippets in kernel/server/serve.go performs a bare filepath.Join(util.SnippetsPath, filePath) on the single-decoded c.Request.URL.Path and serves the result with c.File(), with NO IsSubPath containment and NO IsSensitivePath denylist - unlike the sibling /export/ (serveExport) and /appearance/ (serveAppearance) handlers, which both carry IsSubPath, and unlike /assets/ (serveAssets), whose traversal was fixed in GHSA-p4m3-mgmm-c664. Because util.SnippetsPath = WorkspaceDir/data/snippets, an authenticated request to GET /snippets/%2e%2e/%2e%2e/conf/conf.json resolves to WorkspaceDir/conf/conf.json and leaks the kernel API token and AccessAuthCode (the same secret file CVE-2026-30869 leaked from /export/); GET /snippets/%2e%2e/%2e%2e/temp/siyuan.db leaks the full document database.

Affected versions
-----------------
v3.6.5 and current master (verified by direct source read). The /export/ and /assets/ fixes were endpoint-scoped and never reached serveSnippets.

Technical detail
----------------
Sink, kernel/server/serve.go, serveSnippets (verbatim, current master and v3.6.5):

  func serveSnippets(ginServer *gin.Engine) {
      ginServer.Handle("GET", "/snippets/*filepath", model.CheckAuth, func(c *gin.Context) {
          filePath := strings.TrimPrefix(c.Request.URL.Path, "/snippets/")
          if !model.IsAdminRoleContext(c) {
              if "conf.json" == filePath {
                  c.Status(http.StatusUnauthorized)
                  return
              }
          }
          ext := filepath.Ext(filePath)
          name := strings.TrimSuffix(filePath, ext)
          confSnippets, err := model.LoadSnippets()
          ...
          for _, s := range confSnippets {
              if s.Name == name && ("" != ext && s.Type == ext[1:]) {
                  c.Header("Content-Type", mime.TypeByExtension(ext))
                  c.String(http.StatusOK, s.Content)
                  return
              }
          }
          // when not matched in the config file, look it up on the filesystem
          filePath = filepath.Join(util.SnippetsPath, filePath)   // <-- TAINTED join, no containment
          c.File(filePath)                                        // <-- arbitrary workspace file read
      })
  }

Taint path, end to end:
1. Route GET /snippets/*filepath is registered with the single middleware model.CheckAuth (authentication only; NO CheckAdminRole).
2. c.Request.URL.Path is the request path AFTER Go net/http has percent-decoded it ONCE. The kernel runs gin.New() with default settings (UseRawPath = false, UnescapePathValues = true) and installs NO path-sanitizing middleware (the global ginServer.Use(...) chain is ControlConcurrency, Timing, Recover, corsMiddleware(), jwtMiddleware, gzip, sessions only - none cleans or rejects ..). net/http does not path.Clean URL.Path for gin handlers, so a single-encoded %2e%2e arrives at the handler as a literal .. segment.
3. filePath := strings.TrimPrefix(c.Request.URL.Path, "/snippets/") yields the attacker-controlled remainder, e.g. ../../conf/conf.json.
4. The non-admin guard checks only "conf.json" == filePath; with traversal the value is "../../conf/conf.json", so the guard does not fire (and admins are not checked at all).
5. The config-snippet name/ext loop does not match a traversal string, so control falls through to the filesystem branch.
6. filePath = filepath.Join(util.SnippetsPath, filePath): Go's filepath.Join runs Clean, which RESOLVES .. segments. Clean("WorkspaceDir/data/snippets" + "/../../conf/conf.json") = WorkspaceDir/conf/conf.json. There is no IsSubPath confinement, so the resolved path escapes the snippets root.
7. c.File(filePath) streams the resolved file to the response body.

Directory layout (confirmed by kernel/util/working.go):
  WorkspaceDir/
    data/snippets/  = util.SnippetsPath  (the /snippets/ base)
    conf/conf.json  <-- API token + AccessAuthCode (the secret)
    temp/siyuan.db  <-- full SQLite database
From util.SnippetsPath = WorkspaceDir/data/snippets the climb-out is exactly two levels:
- GET /snippets/%2e%2e/%2e%2e/conf/conf.json -> WorkspaceDir/conf/conf.json (kernel API token, AccessAuthCode, cookie signing material - the same secrets CVE-2026-30869 leaked).
- GET /snippets/%2e%2e/%2e%2e/temp/siyuan.db -> WorkspaceDir/temp/siyuan.db (the entire document database).
- GET /snippets/%2e%2e/%2e%2e/%2e%2e/etc/passwd (and deeper) reaches host files outside the workspace; c.File serves any path Clean resolves to, subject only to OS file permissions.

Incomplete-fix lineage (patch-diff)
-----------------------------------
SiYuan has been fixing path traversal in file-serving handlers ONE endpoint at a time:
- /export/ (serveExport): CVE-2026-30869 (IsSensitivePath denylist, v3.5.10), then CVE-2026-41894 / GHSA-hjh7-r5w8-5872 (double-encode bypass, v3.6.5). Now has IsSubPath(exportBaseDir, fullPath) + IsSensitivePath.
- /appearance/ (serveAppearance): hardened alongside; has IsSubPath(appearancePath, filePath).
- /assets/*path (serveAssets): GHSA-p4m3-mgmm-c664; delegates to model.GetAssetAbsPath (containment) + publish-access check.
- /snippets/*filepath (serveSnippets): NONE. NO IsSubPath, NO IsSensitivePath; only a literal "conf.json" string match for non-admins, defeated by traversal.
The fixes that closed /export/ and /assets/ were endpoint-scoped (per-handler IsSubPath/IsSensitivePath/GetAssetAbsPath) rather than a shared request-level path-confinement primitive applied to every c.File/http.ServeFile sink. serveSnippets was never touched. It reaches the SAME secret file (conf/conf.json) the parent CVE-2026-30869 was filed for, at a LOWER bar in one respect: it needs only single URL encoding (no double-encode trick), because there is no containment check to bypass in the first place.

Privilege / reachability (stated honestly)
------------------------------------------
The route is gated by model.CheckAuth only (any authenticated user), NOT CheckAdminRole. CheckAuth admits any principal that presents a valid API token (Conf.Api.Token), a valid session whose AccessAuthCode == Conf.AccessAuthCode, or BasicAuth. The handler's own if !model.IsAdminRoleContext(c) branch confirms non-admin reachability; that branch only blocks the literal string "conf.json", which the traversal payload "../../conf/conf.json" does not match, so even non-admins leak the secret file. SiYuan supports non-admin authenticated roles (RoleEditor, RoleReader) in shared/published workspace modes, plus access-auth-code logins. Privilege required: PR:L (a valid authenticated session), NOT pre-auth and NOT admin-gated. Reading conf/conf.json yields the admin API token/AccessAuthCode, letting a non-admin escalate to full kernel-admin API control; siyuan.db leaks all note content. The kernel HTTP server is the published interface for self-hosted/Docker deployments (AV:N).

SiYuan's SECURITY.md excludes arbitrary file WRITE outside the workspace as a non-issue, but this finding is arbitrary file READ of in-workspace secrets (conf/conf.json, siyuan.db) and host files. Read-side traversal of conf.json is exactly what CVE-2026-30869 was accepted for, so this is squarely in scope.

Non-destructive: no weaponized exploit is included; the chain is described in prose for the maintainer to reproduce.

Secondary (reported for completeness, not the headline): serveRepoDiff (/repo/diff/*path) shares the same bare filepath.Join(util.TempDir, "repo", "diff", requestPath) + http.ServeFile with NO containment, so .. in requestPath escapes TempDir/repo/diff. BUT it carries model.CheckAdminRole (admin-only), so the trust boundary crossed is weak (an admin already holds the API token). Lower severity; shares the same one-line fix.

Impact
------
Authenticated (non-admin, PR:L) arbitrary workspace file read: kernel API token + AccessAuthCode (conf/conf.json), the full document database (siyuan.db), and host files outside the workspace. Leaking conf.json enables escalation to full kernel-admin API control (and, per the parent CVE, can be chained toward RCE).

Novelty
-------
GitHub Security Advisories for siyuan-note/siyuan include GHSA-2h2p-mvfx-868w / CVE-2026-30869 (/export/), GHSA-hjh7-r5w8-5872 / CVE-2026-41894 (/export/ double-encode), GHSA-p4m3-mgmm-c664 (/assets/ double-encode), plus stored-XSS/template-injection advisories. NONE references /snippets/ or serveSnippets. OSV / GitLab Advisory Database for the Go module github.com/siyuan-note/siyuan/kernel lists only the /export/ and /assets/ path-traversal entries. Not a duplicate; the contribution is the distinct, unpatched sibling handler serveSnippets reached at a non-admin authenticated privilege.

Remediation
-----------
Add the same containment SiYuan already uses in serveExport/serveAppearance: resolve filePath and reject if !gulu.File.IsSubPath(util.SnippetsPath, resolved), and apply util.IsSensitivePath. The identical one-line containment also closes the admin-only /repo/diff/*path (serveRepoDiff) handler.

CWE: CWE-22 (Path Traversal), related CWE-23 (Relative Path Traversal). CVSS v3.1 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N).

Coordinated-disclosure terms: 90 days from acknowledgement before public disclosure, aligned earlier if a fix ships sooner. No public issue / PR / gist / post has been or will be opened before a coordinated date or a shipped fix. No weaponized PoC has been shared.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-275h-v5h9-vr82
- https://nvd.nist.gov/vuln/detail/CVE-2026-59832
- https://github.com/siyuan-note/siyuan/commit/68cc0f537dfa4502496dfa794e71835421c25c09
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/releases/tag/v3.7.1
