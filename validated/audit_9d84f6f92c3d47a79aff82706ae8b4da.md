### Title
Session-key private keys are persisted to disk/browser storage in cleartext, exposing the key used to authorize `SelectSolver` intent fills - (File: `sdk/packages/sdk/src/storage/index.ts`)

### Summary
This is a valid analog to CVE-2022-31085 (LDAP Account Manager persisting credentials in cleartext session files). The `hyperbridge` intents SDK's `createSessionKeyStorage` writes ephemeral order session-key private keys as plain `JSON.stringify` blobs, with no encryption at rest, to whichever backing store the environment resolves to — a plaintext file on disk (Node), `localStorage`, or `indexedDB`.

### Finding Description
`OrderPlacer.placeOrder` generates a fresh EOA private key per order (`generatePrivateKey()`), and immediately persists it via `sessionKeyStorage.setSessionKeyByAddress`: [1](#0-0) 

The storage layer serializes the raw `privateKey` field with no encryption and writes it under a predictable key prefix (`session-key:` / `session-key-address:`): [2](#0-1) [3](#0-2) 

For the Node/CLI/backend consumers of the SDK (the intent filler, solvers, or any backend integration), the driver used is the filesystem driver, which writes these plaintext blobs to `./.hyperbridge-cache` by default with no encryption option exposed: [4](#0-3) [5](#0-4) 

For browser consumers, `detectEnvironment()` selects `localStorage` or `indexedDB`, both of which are also plaintext and readable by any script running in that origin (e.g. via XSS or a malicious dependency): [6](#0-5) 

This session key is not cosmetic — it is the signer of the `SelectSolver` message that authorizes a specific solver to fill the order, cached and reused by `BidImpl`: [7](#0-6) 

No option in `SessionKeyStorageOptions`/`CancellationStorageOptions` provides an encryption-at-rest mechanism, and no wiping/zeroing of the plaintext key occurs when it is no longer needed. The class of bug mirrors LAM's: sensitive authorization secrets are written to a persistent store in cleartext by default, with encryption being neither the default nor enforced.

### Impact Explanation
Any process, user, or script with read access to the storage location (a shared/misconfigured file system, another origin-scoped script via a supply-chain or XSS vector reading `localStorage`/`indexedDB`, a container/host with unrestricted `./.hyperbridge-cache` access, or backup/log exfiltration of that directory) can recover the raw session private key. With it, an attacker can forge/replay a `SelectSolver` signature for the associated order, potentially steering solver selection and interfering with intent fills that the legitimate session key was meant to gate — a concrete unauthorized app action against the intents flow. The direct monetary blast radius is bounded by what a `SelectSolver` signature controls (solver selection for that specific order) rather than the user's main wallet, since the session key is ephemeral and unrelated to the funding key.

### Likelihood Explanation
Likelihood is moderate: exploitation requires an attacker to gain read access to the SDK's storage backend (filesystem path, browser storage, or IndexedDB), which is a plausible but non-trivial precondition (e.g., XSS in a dApp embedding the SDK, a compromised dependency, shared hosting with insufficient FS isolation, or unencrypted device/backup exposure). No cryptographic verification or on-chain safeguard mitigates disclosure once the plaintext key is read, since possessing the key is sufficient to sign `SelectSolver` messages.

### Recommendation
Encrypt session-key material at rest before persisting it (e.g., derive a symmetric key from a user-supplied passphrase/OS keychain and encrypt the JSON blob in `setSessionKey`/`setSessionKeyByAddress`), add secure-storage options (OS keychain/webcrypto-backed encrypted storage) as the default driver rather than plain `fs`/`localStorage`, and proactively remove/rotate session keys immediately after the `SelectSolver` signature is no longer needed rather than leaving them indefinitely in the cache directory.

### Proof of Concept
1. Run any SDK consumer (e.g., the CLI/backend using `OrderPlacer.placeOrder`) so it calls `createSessionKeyStorage()` under Node.
2. Observe that `./.hyperbridge-cache` (or the custom `basePath`) now contains files named by the `session-key:<commitment>` / `session-key-address:<address>` keys whose contents are plaintext JSON containing `privateKey`.
3. Read the file directly (`cat ./.hyperbridge-cache/session-key:*`) to recover the raw hex private key without needing any credentials.
4. Use `privateKeyToAccount(privateKey)` (as the SDK itself does in `OrderPlacer.ts` line 101) to reconstruct the signer and forge a `SelectSolver` signature for that order's bids, exactly as `BidImpl.sign()`/`selectBid` would. [1](#0-0) [5](#0-4)

### Citations

**File:** sdk/packages/sdk/src/protocols/intents/OrderPlacer.ts (L100-110)
```typescript
		const privateKey = generatePrivateKey()
		const account = privateKeyToAccount(privateKey)
		const sessionKeyAddress = account.address as HexString
		const createdAt = Date.now()
		const placementOrder: Order = { ...order, session: sessionKeyAddress }

		await this.ctx.sessionKeyStorage.setSessionKeyByAddress(sessionKeyAddress, {
			privateKey: privateKey as HexString,
			address: sessionKeyAddress,
			createdAt,
		})
```

**File:** sdk/packages/sdk/src/storage/index.ts (L54-59)
```typescript
const detectEnvironment = (): StorageDriverKey => {
	if (typeof process !== "undefined" && !!process.versions?.node) return "node"
	if (typeof globalThis !== "undefined" && "localStorage" in globalThis) return "localstorage"
	if (typeof globalThis !== "undefined" && "indexedDB" in globalThis) return "indexeddb"
	return "memory"
}
```

**File:** sdk/packages/sdk/src/storage/index.ts (L188-210)
```typescript
export interface SessionKeyData {
	/**
	 * The private key as a hex string
	 */
	privateKey: HexString

	/**
	 * The derived public address
	 */
	address: HexString

	/**
	 * The order commitment this session key is associated with.
	 * This may be undefined for session keys that were created
	 * but whose corresponding order has not been finalized yet.
	 */
	commitment?: HexString

	/**
	 * Timestamp when the session key was created
	 */
	createdAt: number
}
```

**File:** sdk/packages/sdk/src/storage/index.ts (L261-272)
```typescript
	const setSessionKey = async (commitment: HexString, data: SessionKeyData): Promise<void> => {
		const storageKey = `${SESSION_KEY_PREFIX}${commitment}`
		await baseStorage.setItem(storageKey, JSON.stringify(data))
	}

	/**
	 * Stores a session key for a session key address
	 */
	const setSessionKeyByAddress = async (address: HexString, data: SessionKeyData): Promise<void> => {
		const storageKey = `${SESSION_KEY_ADDRESS_PREFIX}${address.toLowerCase()}`
		await baseStorage.setItem(storageKey, JSON.stringify(data))
	}
```

**File:** sdk/packages/sdk/src/storage/load-driver.ts (L1-3)
```typescript
// Important: DO NOT REMOVE or RENAME this module
// Note: uses only Node driver during development.
export { loadDriver } from "./drivers/node"
```

**File:** sdk/packages/sdk/src/storage/drivers/node.ts (L1-6)
```typescript
import fsDriver from "unstorage/drivers/fs"
import type { LoadDriver } from "../types"

export const loadDriver: LoadDriver = ({ options }) => {
	return fsDriver({ base: options?.basePath ?? "./.hyperbridge-cache" })
}
```

**File:** sdk/packages/sdk/src/protocols/intents/Bid.ts (L56-87)
```typescript
	private readonly sessionPrivateKey?: HexString

	private readonly intentGatewayV2Address: HexString
	private readonly domainSeparator: HexString

	/** Cached session-key signature over the `SelectSolver` message. */
	private cachedSignature?: HexString

	constructor(params: BidParams) {
		this.ctx = params.ctx
		this.crypto = params.crypto
		this.order = params.order
		this.fillOptions = params.fillOptions
		this.priceOutputs = params.priceOutputs
		this.sessionPrivateKey = params.sessionPrivateKey

		this.solverAddress = params.fillerBid.userOp.sender
		this.outputs = params.fillOptions.outputs
		this.relayerFee = params.fillOptions.relayerFee
		this.nativeDispatchFee = params.fillOptions.nativeDispatchFee
		this.userOp = params.fillerBid.userOp

		this.intentGatewayV2Address = this.ctx.dest.configService.getIntentGatewayAddress(
			normalizeStateMachineId(this.order.destination),
		)
		this.domainSeparator = CryptoUtils.getDomainSeparator(
			"IntentGateway",
			"2",
			this.chainId(),
			this.intentGatewayV2Address,
		)
	}
```
