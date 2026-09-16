### Title
Arbitrary config file write via attacker-controlled `path` in `/api/setup/save-and-start` - (File: `sdk/packages/simplex/src/services/server/setup-api.ts`)

### Summary
The `simplex` UI server's setup wizard endpoint `save-and-start` writes an attacker-influenced TOML document to an attacker-supplied filesystem path with no path validation, mirroring the CVE's root cause of "filtering user parameters before passing them into" a file-writing routine, letting a caller "create a file with a custom filename and content."

### Finding Description
`handleSetupRequest` dispatches `POST /api/setup/save-and-start` to `saveAndStart` [1](#0-0) . Inside `saveAndStart`, the destination path is taken directly from the untrusted JSON body with only a `trim()` check — no allow-list, no containment to a data directory, no rejection of `..` or absolute paths: [2](#0-1) 

The content written, `result.toml`, comes from `gateConfig(body)`, which mostly just re-serializes the attacker-supplied `body.config` object via `emitFillerToml` after light schema validation (`validateSignerConfig`, `validateRpcUrls`, `validateConfig`) [3](#0-2) . None of that validation constrains the destination path or the arbitrary string fields (RPC URLs, bundler URLs, signer fields, etc.) that end up embedded verbatim in the emitted file via `writeConfigFileAtomic` [4](#0-3) .

This is directly analogous to CVE-2019-1010123's root cause: a web-reachable endpoint accepts user-controlled filename/path and content parameters and passes them into a file-write routine without restricting the target location or type/content, "creating file with custom a filename and content."

### Impact Explanation
An attacker who can reach the `init`-mode UI server's HTTP API (the setup wizard server that runs before the filler is fully bootstrapped) can direct `writeConfigFileAtomic` to write/overwrite an arbitrary file on the host filesystem that the `simplex` process user can write to, using `path` traversal (e.g., `../../.ssh/authorized_keys`-style paths or any absolute path) and content shaped through the config-emission pipeline. Because `save-and-start` also triggers `setup.onSaveAndStart`, which starts the filler using that written file as its config, this can also be leveraged to make the filler load an operator-crafted config (e.g. redirecting `hyperbridgeWsUrl`, RPC URLs, or signer material) — a config/asset integrity issue for a component that signs and submits solver bids and controls funds transfers across the intents/filler pipeline. Depending on filesystem permissions this ranges from local config-poisoning up to file overwrite of sensitive files reachable by the process user.

### Likelihood Explanation
Exploitability depends on network exposure of the `init`-mode server. Tests show the server enforces a loopback-only bind for `init` mode (`server.start(0, "0.0.0.0")` rejects with "loopback" error), which substantially limits remote exploitability to same-host or tunnel/proxy-forwarded access [5](#0-4) . However, any local/tunnelled attacker or CSRF-style request from a malicious page open on the operator's machine reaching `127.0.0.1` during the setup phase can invoke this endpoint before the wizard's normal browser-driven flow completes, since the endpoint performs no path allow-listing itself.

### Recommendation
- In `saveAndStart` (`setup-api.ts`), stop trusting `body.path` as a raw filesystem path. Resolve it against a fixed, expected data directory and reject/normalize any result that escapes that directory (mirrors the existing traversal guard already used for static file serving in `serveStatic`, see `sdk/packages/simplex/src/services/server/static.ts:26-39`).
- If a caller-chosen filename is required, generate/derive it server-side or strictly validate it against a filename-only pattern (no path separators, no `..`).
- Add the same tunnel/`Origin` or CSRF-token protections already noted for the socket bind and the mutating operator PUT endpoints to the `/api/setup/*` POST routes, if not already applied uniformly.

### Proof of Concept
Against a running `init`-mode `simplex` UI server (bound to loopback), send:
```
POST /api/setup/save-and-start HTTP/1.1
Host: 127.0.0.1:<port>
Content-Type: application/json

{
  "path": "../../../../tmp/evil-config.toml",
  "config": { "simplex": { "watchOnly": true, "maxConcurrentOrders": 1, "hyperbridgeWsUrl": "" }, "chains": [] }
}
```
`gateConfig` accepts a minimal watch-only config (no signer required) and passes validation [6](#0-5) , after which `writeConfigFileAtomic(path, result.toml)` writes the emitted TOML to the traversed path outside the intended config directory [7](#0-6) .

### Citations

**File:** sdk/packages/simplex/src/services/server/setup-api.ts (L130-131)
```typescript
			case "save-and-start":
				return saveAndStart(server, setup, body, res)
```

**File:** sdk/packages/simplex/src/services/server/setup-api.ts (L287-320)
```typescript
function gateConfig(body: Record<string, unknown>): GatedConfig | { ok: false; error: string } {
	const config = body.config as FillerConfigFile | undefined
	const chainLabels = Array.isArray(body.chainLabels) ? body.chainLabels.map(String) : undefined
	// Enabled chain ids, sent by the wizard so boot-parity symbol resolution can
	// run offline. Advisory for early feedback — boot re-checks against the
	// chains actually resolved from the RPCs.
	const chainIds = Array.isArray(body.chainIds) ? body.chainIds.map(Number).filter(Number.isFinite) : []
	if (!config || typeof config !== "object") return { ok: false, error: "Missing config object" }
	try {
		// The same rule `run` applies: a signer block is required unless the config
		// is globally watch-only, and a present block is validated for completeness.
		if (config.simplex?.signer) {
			validateSignerConfig(config.simplex.signer)
		} else if (config.simplex?.watchOnly !== true) {
			throw new Error("Signer configuration is required via [simplex.signer]")
		}
		for (const chain of config.chains ?? []) validateRpcUrls(chain.rpcUrls)
		validateConfig(config)
		if (chainIds.length > 0 && config.pairs?.length) {
			assertPairSymbolsResolve(
				config.pairs,
				new AssetRegistry(new ChainConfigService({}), config.assets),
				chainIds.map(formatChainKey),
			)
		}
		if (chainIds.length > 0) {
			assertConfirmationCoverage(config.confirmationPolicies, chainIds)
		}
		const toml = emitFillerToml(config, { chainComments: chainLabels })
		return { config, toml, chainLabels }
	} catch (err) {
		return { ok: false, error: err instanceof Error ? err.message : String(err) }
	}
}
```

**File:** sdk/packages/simplex/src/services/server/setup-api.ts (L366-378)
```typescript
function saveAndStart(server: UiServer, setup: SetupContext, body: Record<string, unknown>, res: ServerResponse): void {
	if (server.getStartState() === "starting") {
		return sendJson(res, 409, { error: "A start is already in progress" })
	}
	const result = gateConfig(body)
	if ("error" in result) return sendJson(res, 400, result)

	const path = typeof body.path === "string" && body.path.trim() ? body.path.trim() : setup.configPath
	try {
		writeConfigFileAtomic(path, result.toml)
	} catch (err) {
		return sendJson(res, 500, { error: `Could not write ${path}: ${err instanceof Error ? err.message : err}` })
	}
```

**File:** sdk/packages/simplex/src/cli/init/emit-toml.ts (L13-25)
```typescript
export function writeConfigFileAtomic(path: string, content: string): void {
	const tempPath = join(dirname(path), `.${basename(path)}.${randomBytes(6).toString("hex")}.tmp`)
	try {
		writeFileSync(tempPath, content, { mode: 0o600 })
		chmodSync(tempPath, 0o600)
		renameSync(tempPath, path)
	} catch (error) {
		try {
			unlinkSync(tempPath)
		} catch {}
		throw error
	}
}
```

**File:** sdk/packages/simplex/src/tests/ui-server.test.ts (L1735-1741)
```typescript
	it("refuses non-loopback binds", async () => {
		server = new UiServer({
			mode: "init",
			setup: { configPath: "/tmp/x.toml", onSaveAndStart: async () => {} },
		})
		await expect(server.start(0, "0.0.0.0")).rejects.toThrow(/loopback/)
	})
```
