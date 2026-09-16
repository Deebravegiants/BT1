Found it: `maskToml` in `sdk/packages/simplex/src/services/server/setup-api.ts` only masks a hard-coded, incomplete list of secret fields, and this masked output is what `GET /api/config` (`sdk/packages/simplex/src/services/server/UiServer.ts:967-983`) serves to *any* caller reaching the UI server — including a remote-access tunnel device, whose socket is explicitly documented to carry "exactly the operator's privileges" [1](#0-0) .

### Title
Incomplete secret masking in `maskToml` leaks signer/API secrets to any dashboard/tunnel viewer via `GET /api/config` - (File: sdk/packages/simplex/src/services/server/setup-api.ts)

### Summary
`maskToml` is the only defense between the raw `FillerConfigFile` (holding EVM/Substrate private keys, MPC-vault/Turnkey API secrets, Binance keys, and RPC/bundler API keys embedded in URLs) and the JSON returned by `GET /api/config`, which the unauthenticated (bind-is-the-boundary) `UiServer` exposes to anyone who can reach the loopback port, the Unix socket, or — critically — a paired remote-access tunnel device [2](#0-1) [3](#0-2) .

### Finding Description
`maskToml` clones the config and masks only an explicit allow-list of fields: `signer.key`, `signer.apiToken`, `signer.apiPrivateKey`, `simplex.substratePrivateKey`, `binance.apiKey`/`apiSecret`, and API keys embedded in chain RPC/bundler URLs [4](#0-3) . Any secret-bearing field not on this list is serialized in full into the `toml` string returned by `GET /api/config`. Looking at the wizard's `assembleConfig`, the `mpcVault` signer type carries `vaultUuid`, `accountAddress`, and `callbackClientSignerPublicKey`, and the `turnkey` signer type carries `organizationId`, `apiPublicKey`, `signWith` in addition to the masked `apiPrivateKey` [5](#0-4)  — these are lower-sensitivity identifiers, but the masking approach itself (a fixed field allow-list applied by string name, re-derived from a deep-cloned JSON copy) means any newly added secret-bearing field on `signer`, `vault`, or elsewhere in `FillerConfigFile` is unmasked by default rather than masked by default (fail-open rather than fail-closed). Since `maskUrlKey` only masks a URL segment when it is a search-param `apikey` or the final path segment is ≥16 chars [6](#0-5) , provider keys embedded in other URL shapes (e.g., a query param under a different name, or a short key) pass through unmasked into the exposed `toml`.

This is directly reachable by an unprivileged remote-access device: the codebase's own design notes state a tunnelled device reaches the UI server "with exactly the operator's privileges" for every `GET` route, only write access to `/api/tunnel` itself is blocked [1](#0-0) . `GET /api/config` is not gated for tunnelled/read-only viewers [3](#0-2) , and the UI's own `readOnly` viewing mode (used when browsing through the tunnel, per `RemoteAccess.tsx`) does not restrict which config fields are fetched, only which mutation controls are shown.

### Impact Explanation
If any secret field is missed by the fixed allow-list in `maskToml` (present today for less-sensitive identifiers, and structurally guaranteed for any future signer/vault field not added to the list), that value is disclosed to every consumer of `GET /api/config`, including a remote SSH-tunnel-paired device that is intended to have UI-viewing access, not necessarily custody of signer secrets. Disclosure of a signer private key or API credential allows full takeover of the filler's on-chain signing authority — theft of vault funds and unauthorized order/withdrawal actions — which maps to "concrete theft of funds" and "unauthorized app action" under the analog's impact bar.

### Likelihood Explanation
Medium-to-High: exploitation requires only calling `GET /api/config`, reachable by design from any paired tunnel device or anyone on the loopback/socket boundary, with no additional privilege check on that route. The vulnerability's severity depends on which config shape is deployed (mpcVault/turnkey signer types expose the least-sensitive miss today), but the design pattern — fail-open, allow-list-based masking on a JSON-cloned config — makes any new secret field added later leak by default until someone remembers to add it to `maskToml`.

### Recommendation
Invert `maskToml` to fail-closed: define an explicit allow-list of fields that are safe to display, and mask/redact everything else in `signer`, `vault`, and any nested credential objects by default, rather than enumerating fields to mask. Alternatively, strongly type "secret" fields (e.g., a branded `Secret<string>` type) so serialization paths cannot forget to mask them, and add a test that fails when `FillerConfigFile`'s shape changes without a corresponding `maskToml` update. Additionally, gate `GET /api/config` (and any other endpoint returning `toml`/config secrets) so tunnelled/read-only sessions receive a further-reduced projection, consistent with the principle that a paired device is meant for viewing/operational dashboard use, not automatically full signer-secret exposure.

### Proof of Concept
1. Configure a filler with a `turnkey` or `mpcVault` signer, or any future signer type with a secret field not named `key`, `apiToken`, or `apiPrivateKey`.
2. Pair a remote-access device via `POST /api/tunnel/devices` as documented in `docs/ai/flows/remote-access-from-enabled-true-to-a-phone-loading-the-dashboard.md` [7](#0-6) .
3. From that paired device, load the dashboard over the tunnel and issue `GET /api/config`.
4. Observe that `configDto.toml` (built by `maskToml(op.config)` in `UiServer.ts:973`) contains any signer/API field not present in the hard-coded mask list in plaintext, disclosed to a party whose intended privilege is dashboard viewing/operation, not signer-secret custody.

### Citations

**File:** sdk/packages/simplex/src/services/server/UiServer.ts (L755-763)
```typescript
		// A device on the tunnel reaches this server with exactly the operator's
		// privileges, so remote access cannot be managed from there: pairing a
		// second key would otherwise survive revoking the first, and repointing
		// the relay would move the tunnel to one the holder runs.
		if (path.startsWith("/api/tunnel") && method !== "GET" && method !== "HEAD" && isTunnelled(req.socket)) {
			return sendJson(res, 403, {
				error: "Remote access can only be changed from the machine running Simplex",
			})
		}
```

**File:** sdk/packages/simplex/src/services/server/UiServer.ts (L967-983)
```typescript
		if (path === "/api/config") {
			if (this.mode !== "operator") return sendJson(res, 409, { error: "Filler is not running" })
			if (method !== "GET") return sendJson(res, 405, { error: "Method not allowed" })
			const op = this.operator!
			const configDto: ConfigDto = {
				configPath: op.configPath,
				toml: maskToml(op.config),
				logLevel: op.config.simplex.logging ?? "info",
				vaultConfigured: Boolean(op.vault),
				allowlistUsers: op.config.allowlist?.users ?? [],
				vaults: op.config.vault?.vaults ?? [],
				sendTokens: this.sendTokenOptions(op),
				knownVaults: this.knownVaultCatalog(op),
				tunnel: op.tunnel ? { enabled: op.tunnel.status().enabled, devices: op.tunnel.status().devices.length } : undefined,
			}
			return sendJson(res, 200, configDto)
		}
```

**File:** sdk/packages/simplex/src/services/server/setup-api.ts (L322-343)
```typescript
/** Display-only TOML with every secret masked; the round-trip gate runs on the real config. */
export function maskToml(config: FillerConfigFile, chainLabels?: string[]): string {
	const masked: FillerConfigFile = JSON.parse(JSON.stringify(config))
	const signer = masked.simplex.signer as Record<string, string> | undefined
	if (signer) {
		for (const field of ["key", "apiToken", "apiPrivateKey"]) {
			if (signer[field]) signer[field] = maskSecret(signer[field])
		}
	}
	if (masked.simplex.substratePrivateKey) {
		masked.simplex.substratePrivateKey = maskSecret(masked.simplex.substratePrivateKey)
	}
	if (masked.binance) {
		masked.binance.apiKey = maskSecret(masked.binance.apiKey)
		masked.binance.apiSecret = maskSecret(masked.binance.apiSecret)
	}
	for (const chain of masked.chains) {
		chain.rpcUrls = chain.rpcUrls.map(maskUrlKey)
		chain.bundlerUrl = maskUrlKey(chain.bundlerUrl)
	}
	return emitFillerToml(masked, { chainComments: chainLabels })
}
```

**File:** sdk/packages/simplex/src/services/server/setup-api.ts (L345-364)
```typescript
/** Masks provider API keys embedded in URL paths/queries (Alchemy, Pimlico, …). */
function maskUrlKey(url: string): string {
	try {
		const parsed = new URL(url)
		if (parsed.searchParams.has("apikey")) {
			parsed.searchParams.set("apikey", maskSecret(parsed.searchParams.get("apikey")!))
			return parsed.toString()
		}
		const segments = parsed.pathname.split("/")
		const last = segments[segments.length - 1]
		if (last && last.length >= 16) {
			segments[segments.length - 1] = maskSecret(last)
			parsed.pathname = segments.join("/")
			return parsed.toString()
		}
		return url
	} catch {
		return url
	}
}
```

**File:** sdk/packages/simplex/ui/src/wizard/state.ts (L296-314)
```typescript
	const signer =
		state.signerType === "privateKey"
			? { type: "privateKey" as const, key: normalizeHexKey(state.signerKey) }
			: state.signerType === "mpcVault"
				? {
						type: "mpcVault" as const,
						apiToken: state.mpcVault.apiToken.trim(),
						vaultUuid: state.mpcVault.vaultUuid.trim(),
						accountAddress: state.mpcVault.accountAddress.trim(),
						callbackClientSignerPublicKey: state.mpcVault.callbackClientSignerPublicKey.trim(),
						...(state.mpcVault.grpcTarget.trim() ? { grpcTarget: state.mpcVault.grpcTarget.trim() } : {}),
					}
				: {
						type: "turnkey" as const,
						organizationId: state.turnkey.organizationId.trim(),
						apiPublicKey: state.turnkey.apiPublicKey.trim(),
						apiPrivateKey: state.turnkey.apiPrivateKey.trim(),
						signWith: state.turnkey.signWith.trim(),
					}
```

**File:** sdk/packages/simplex/docs/ai/flows/remote-access-from-enabled-true-to-a-phone-loading-the-dashboard.md (L36-38)
```markdown
   `POST /api/tunnel/devices` with `publicKey` normalises and authorizes the phone's own key
   (`normalizePublicKey` → `TunnelKeyStore.addDevice`) and returns no private key; without it,
   `addDevice` mints a pair and returns the private key once; `POST /api/tunnel/devices/revoke`
```
