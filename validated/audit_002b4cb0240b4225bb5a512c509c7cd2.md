### Title
Path-traversal in `serveStatic`'s directory guard via bare `startsWith` prefix bypass - (File: sdk/packages/simplex/src/services/server/static.ts)

### Summary
`serveStatic` restricts served files to `uiDistDir` by checking `requested.startsWith(root)` after resolving the requested path, but this check does not verify a path separator boundary, so a sibling directory whose name shares the root's prefix bypasses the guard, analogous to CVE-2022-2479's "insufficient validation of untrusted input... allowed access to internal file directories via a crafted [request]."

### Finding Description
`serveStatic` computes `root = resolve(uiDistDir)` and `requested = resolve(join(root, decodedPath))`, then only serves the file if `requested.startsWith(root)` [1](#0-0) . This is a bare string-prefix check with no trailing separator normalization: if `root` is e.g. `/home/user/app/dist`, a decoded path that resolves outside it to a sibling like `/home/user/app/dist-secrets/...` still satisfies `startsWith(root)` because `"...dist-secrets".startsWith("...dist")` is true as a string comparison. The `docs/ai/changelog/2026-09-09-security-audit-fixes-for-the-unix-socket-listen-mode-1245.md` changelog for this same server explicitly records this as a known, unfixed defect: "the stale `once("error")` handler... `serveStatic`'s traversal guard uses a bare `startsWith`" [2](#0-1) . The route is invoked from `UiServer.handle` to serve any GET request for a path not matched by a more specific API route (the SPA fallback), which is unauthenticated by design ("Unauthenticated: binding is the boundary") [3](#0-2) .

### Impact Explanation
This is a local information-disclosure bug in the Simplex intent-solver's operator dashboard/HTTP server, not a fund-custody or bridge-consensus path: it can leak files sitting in a sibling directory of the compiled SPA bundle on the operator's machine (e.g., a poorly named directory such as `dist-secrets` next to `dist`) to any caller able to reach the socket/port. The existing test suite already validates the naive `../secret.txt` case is blocked [4](#0-3) , but does not cover the sibling-prefix bypass, so the gap is real but narrow (it requires an adjacent directory whose name is a prefix-extension of `dist`, which is not the layout Simplex ships — `uiDistDir` is the build's own dist folder).

### Likelihood Explanation
Exploitability depends entirely on deployment layout: it requires a sibling directory sharing `root`'s name as a string prefix (e.g. `dist` vs `dist-old`) to exist alongside the UI's dist directory, which is not guaranteed and not the shipped configuration. Additionally, per `UiServer`'s own design notes, the server binds to loopback or a `0600` Unix socket by default and treats the bind itself as the authentication boundary [3](#0-2) [5](#0-4) , so remote/unprivileged network exploitation is not the primary vector; a local, low-privilege user on the same host (or, if an operator misconfigures a non-loopback bind, an attacker on the trusted LAN) would be needed. This is explicitly acknowledged as a known, low-priority residual issue by the maintainers themselves rather than a newly discovered exploitable path.

### Recommendation
Harden the containment check in `serveStatic` to require a path-separator boundary, e.g. `requested === root || requested.startsWith(root + path.sep)`, instead of a bare `startsWith(root)` comparison, closing the sibling-directory prefix bypass.

### Proof of Concept
Given `uiDistDir = "/srv/simplex/dist"` and a directory `/srv/simplex/dist-secrets/leaked.txt` existing alongside it: a request such as `GET /..%2Fdist-secrets%2Fleaked.txt` decodes to `../dist-secrets/leaked.txt`; `join(root, decodedPath)` resolves to `/srv/simplex/dist-secrets/leaked.txt`, and `"/srv/simplex/dist-secrets/leaked.txt".startsWith("/srv/simplex/dist")` evaluates `true`, so the guard at [6](#0-5)  passes and the file outside the intended root is served, mirroring the existing traversal test's structure but using a prefix-colliding sibling name instead of a plain `../`.

### Citations

**File:** sdk/packages/simplex/src/services/server/static.ts (L26-39)
```typescript
export function serveStatic(res: ServerResponse, uiDistDir: string, urlPath: string): boolean {
	const root = resolve(uiDistDir)
	let decodedPath: string
	try {
		decodedPath = decodeURIComponent(urlPath)
	} catch {
		decodedPath = urlPath
	}
	const requested = resolve(join(root, decodedPath === "/" ? "index.html" : decodedPath))
	if (!requested.startsWith(root)) {
		res.writeHead(403, { "Content-Type": "text/plain" })
		res.end("Forbidden")
		return true
	}
```

**File:** sdk/packages/simplex/docs/ai/changelog/2026-09-09-security-audit-fixes-for-the-unix-socket-listen-mode-1245.md (L48-54)
```markdown
Audit findings deliberately not acted on: path squatting (`--ui-socket` has no default, so there is no
well-known path to camp on, and the daemon is fail-closed on a live socket); chmod-through-symlink (the
lstat gate closes it, and the sticky bit forbids the precondition anyway); and TCP-to-socket bridging
(an operator who builds one has already converted a 0600 boundary back into an open port). Pre-existing
issues recorded, not fixed here: the server has no authentication in any mode, `serveStatic`'s traversal
guard uses a bare `startsWith`, and the stale `once("error")` handler swallows the first post-listen
server error.
```

**File:** sdk/packages/simplex/src/services/server/UiServer.ts (L351-357)
```typescript
/**
 * Loopback HTTP server embedded in the simplex process. Serves the bundled SPA
 * and a JSON API in one of two modes: `init` (setup wizard endpoints, before a
 * config exists) or `operator` (status/pause/balances plus inflight price curve
 * updates on the running strategies). Unauthenticated: binding is the boundary —
 * init mode refuses non-loopback hosts outright.
 */
```

**File:** sdk/packages/simplex/src/services/server/UiServer.ts (L624-629)
```typescript
		if (this.mode === "operator" && !isLoopbackHost(host)) {
			this.logger.warn(
				{ host },
				"UI server binding a non-loopback address — it is unauthenticated, make sure the network is trusted",
			)
		}
```

**File:** sdk/packages/simplex/src/tests/ui-server.test.ts (L1193-1196)
```typescript
		// traversal is blocked (fetch normalizes ../, so send the raw path over a socket)
		const traversal = await rawRequest(port, "/../secret.txt")
		expect(traversal).toContain("403")
	})
```
