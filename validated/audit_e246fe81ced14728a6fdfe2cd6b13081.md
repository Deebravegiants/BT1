The strongest analog to this bug class in this codebase is in the Simplex intent-solver's operator/dashboard HTTP server, not in the on-chain ISMP/Hyperbridge protocol contracts. It reproduces the same root-cause pattern as the Cloudflare Vite plugin advisory: a locally-run dev/operator server that serves static files from a directory using an insufficient path-containment check, risking exposure of files outside the intended root — including the filler's signer/config secrets.

### Title
Path traversal in Simplex UI server's static file handler via bare `startsWith` prefix check - (File: `sdk/packages/simplex/src/services/server/static.ts`)

### Summary
`serveStatic()`, used by the Simplex solver's UI/dashboard HTTP server to serve the built SPA, validates that a requested path stays inside the UI dist directory using `requested.startsWith(root)` [1](#0-0)  — the exact bug class flagged in the Cloudflare Vite plugin advisory: a locally-hosted dev/operator server exposing files outside its intended asset root because path containment isn't enforced with a proper separator-aware boundary check.

### Finding Description
`serveStatic` resolves the requested URL path by joining it onto the UI dist directory and containment is checked with a bare string `startsWith(root)` rather than requiring `root + path.sep` as a prefix or using `path.relative` to detect `..` escapes [2](#0-1) . Because `path.join`/`path.resolve` normalize `../` segments before the check runs, a request whose decoded path climbs out of `root` and back into a sibling directory that merely shares `root`'s name as a string prefix (e.g. `root` = `.../dist` and a sibling `.../dist-something`) passes the check, since `"/x/dist-something".startsWith("/x/dist")` is `true`. This is a known, explicitly recorded but *unfixed* gap: the audit changelog for the socket-listen-mode hardening states plainly, "Pre-existing issues recorded, not fixed here: the server has no authentication in any mode, `serveStatic`'s traversal guard uses a bare `startsWith`..." [3](#0-2) . The dashboard/API this file backs is unauthenticated by design — the bind address is the only boundary, and both the docs and README repeatedly warn it is unauthenticated and must not be exposed on a non-loopback interface [4](#0-3) [5](#0-4) . The Docker image's default command binds `0.0.0.0:8686` inside its network namespace, and operators are relied upon to keep the published port restricted to `127.0.0.1` — exactly the class of exposure surface the Cloudflare advisory describes for `npm run dev -- --host 0.0.0.0` or tunnels like `cloudflared` [6](#0-5) .

### Impact Explanation
If the UI server is reachable (misconfigured bind, Docker port published without the loopback prefix, or a remote-access tunnel), an attacker able to place or find a sibling directory near the UI dist root could read arbitrary files served by the process outside the intended asset directory, given the flawed prefix check is the sole containment mechanism [2](#0-1) . Since this server is the same process holding solver secrets and exposing fund-moving endpoints (`/api/send`, vault operations) that are themselves unauthenticated by design [7](#0-6) , any information-disclosure primitive against this server is high-severity in context — it sits next to a fund-drain surface the project's own security audits already treat as sensitive (see the DNS-rebinding and SSH-tunnel-auth-bypass fixes affecting the same server) [8](#0-7) .

### Likelihood Explanation
Exploitability depends on network exposure (misbound host or published Docker port) and on a suitable sibling-directory name existing next to the UI dist root — the project's own security audit already logged this exact `startsWith` weakness as a known, unresolved gap rather than a hypothetical one [3](#0-2) .

### Recommendation
Replace the bare `requested.startsWith(root)` check with a separator-safe containment test, e.g. `path.relative(root, requested)` verified to not start with `..` and not be absolute, or require `requested === root || requested.startsWith(root + path.sep)`.

### Proof of Concept
1. Run `simplex` with the UI server bound to a non-loopback interface (e.g. the Docker default `--ui 0.0.0.0:8686`, or a misconfigured `--ui`).
2. Ensure a directory sibling to `uiDistDir` exists whose name is prefixed by `uiDistDir`'s basename (this can occur from build artifacts, backups, or attacker-influenced deployment layouts).
3. Send a crafted GET request whose decoded path traverses out of `uiDistDir` and back into the sibling directory (e.g. `/..%2Fdist-backup/secret.txt`), which `serveStatic`'s `startsWith(root)` check fails to reject [2](#0-1) .
4. The file is served with its contents disclosed to the requester.

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

**File:** sdk/packages/simplex/README.md (L108-113)
```markdown
Curve changes apply immediately and are written back to the config file (regenerated with standard
comments) so restarts keep them. Venue-priced strategies and disabled sides (one-sided LP) are not
editable. The server is unauthenticated — mutating requests need the `X-Simplex-UI: 1` header (CSRF
hygiene), and both the wizard and the operator UI bind loopback unless told otherwise. Only bind
another interface (e.g. `--ui 0.0.0.0:8686`, which the docker image does inside its own network
namespace) on a trusted network.
```

**File:** docs/content/developers/evm/simplex/dashboard.mdx (L17-23)
```text
It is unauthenticated by design — the bind address is the boundary. It defaults to `127.0.0.1:8686`, so only the machine running the solver can reach it, and it refuses any request whose `Host` header is a DNS name rather than a loopback literal, which closes the DNS-rebinding path into it. Move it with `--ui`, or turn it off with `--no-ui` — see [Command-line flags](#command-line-flags) below.

<Callout type="warn">
    Anyone who reaches the dashboard can pause filling, edit price curves, move treasury funds and
    send tokens out of the wallet. Do not bind it to a public interface, and do not publish its
    Docker port past `127.0.0.1`. The two options below reach it from elsewhere without exposing it.
</Callout>
```

**File:** sdk/packages/simplex/scripts/DOCKERHUB.md (L43-50)
```markdown
## Ports and volumes

`8686` is the web UI and setup wizard. The container's default command binds it to `0.0.0.0` —
a container-local loopback bind is unreachable from the host, and Docker Desktop on macOS and
Windows has no `--network host` to fall back on. The container's network namespace is the boundary,
so the port stays private until published. **Keep the `127.0.0.1:` prefix when publishing**: the UI
is unauthenticated, and the wizard collects private keys. If you override the command, carry
`--ui 0.0.0.0:8686` over with it.
```

**File:** sdk/packages/simplex/src/services/server/UiServer.ts (L721-731)
```typescript
		// Framing defense: the API is unauthenticated by design — the bind is the
		// boundary — so a page that frames this UI never needs to read or script
		// it. It only needs the operator to tap through an invisible overlay: the
		// click lands in the real UI, same-origin, with its own X-Simplex-UI header.
		// That reaches pause, reset-halt and vault sweep/redeem, which are one
		// click each. `frame-ancestors` is the directive browsers honour today;
		// X-Frame-Options is the fallback for older WebViews that ignore CSP.
		// Set here, before anything can return, so 403s carry it too — and via
		// setHeader so every writeHead downstream merges rather than drops it.
		res.setHeader("Content-Security-Policy", "frame-ancestors 'none'")
		res.setHeader("X-Frame-Options", "DENY")
```

**File:** sdk/packages/simplex/docs/ai/changelog/2026-09-05-close-the-dns-rebinding-bypass-in-the-ui-server-s-loopback-host.md (L1-14)
```markdown
# 2026-09-05 — Close the DNS-rebinding bypass in the UI server's loopback Host check

`isLoopbackHost` decided loopback with `host.startsWith("127.")`, a string-prefix test on a
hostname. A leading-digit DNS label is legal, so `127.0.0.1.evil.com` (and `127.evil.com`,
`127.0.0.1.nip.io`, the bare `127.`) passed it. That predicate is the whole of the UI server's
auth — `hostHeaderAllowed` delegates to it on the `boundLoopback` path, and there is no
Origin/CORS check — so a page an operator visits could rebind DNS to `127.0.0.1`, become
same-origin, and reach `POST /api/send` (drains the solver wallet + vault positions) and the
unmasked keys in `GET /api/chains`. Now the host must parse as an IPv4 literal via `node:net`
`isIP` before its `127.` octet is trusted; `localhost`, `::1`, and the IPv4-mapped `::ffff:127.0.0.1`
stay allowed. The same change fixes the `--ui 127.x.evil.com` bind-gate bypass (same function) and
replaces the non-loopback branch's `hostname.includes(":")` IPv6 test with `isIP`, which also
rejects a stray non-numeric port like `evil.com:abc`. Extended the rebinding test with the bypass
vectors; it fails on the old prefix code and passes now (60/60).
```
