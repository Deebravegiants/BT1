### Title
Session key private keys for IntentGatewayV2 solver-selection are persisted unencrypted, allowing theft and unauthorized solver selection - (File: sdk/packages/sdk/src/storage/index.ts)

### Summary
`createSessionKeyStorage` in the Hyperbridge SDK persists the raw hex `privateKey` of an order's session key in plaintext to whatever storage backend the environment resolves to (browser `localStorage`, IndexedDB, or a Node filesystem driver), with no encryption at rest. This session key's signature is later used to authorize which solver fills an intents order, so plaintext, unencrypted persistence of it is analogous to Artemis's CVE-2020-10727 pattern: security-sensitive credentials written to a locally-readable store without protection, letting anyone with local/script read access to that store recover the secret and perform unauthorized actions.

### Finding Description
`createSessionKeyStorage` ( [1](#0-0) ) stores `SessionKeyData` — which includes the plaintext `privateKey: HexString` field ( [2](#0-1) ) — via `JSON.stringify(data)` with no encryption, hashing, or wrapping, directly into the environment-selected `unstorage` driver.

The environment is auto-detected: Node uses a filesystem driver, browsers use `localStorage`/`indexedDB` ( [3](#0-2) ), and no encryption layer wraps any of these drivers ( [4](#0-3)  and [5](#0-4) ). This session key is not a throwaway artifact — `BidImpl.signSelection()` in `sdk/packages/sdk/src/protocols/intents/Bid.ts` fetches it from this storage and uses it to sign the `SelectSolver` message that authorizes a specific solver address to fill (and be paid for) an order ( [6](#0-5) ). This signature is submitted on-chain as part of `IntentGatewayV2.select()` ( [7](#0-6) ), i.e., the session private key is the sole authority determining which solver is entitled to fill and collect the order's payout.

Because the key is written to disk/localStorage unencrypted, any local process, malicious browser extension, XSS payload on the hosting origin, unprotected disk backup, or filesystem access on a shared/Node host can read it directly — mirroring the Artemis flaw where `resetUsers` wrote credentials in plaintext to a locally readable file that any local process could read.

### Impact Explanation
Recovering a session private key lets an attacker sign `SelectSolver` messages for that order's commitment and submit them via `IntentGatewayV2.select()`, unilaterally routing solver selection to an address of their choosing (e.g., their own colluding solver) instead of the legitimate winning bidder. This is an unauthorized app action directly controlling economic outcomes of the intents flow (who gets to fill and earn the reward for an order), satisfying the "unauthorized app action" bar for a valid finding. It does not require any special permission beyond reading storage the SDK itself created — reachable by any actor able to read the local storage of the consuming application (attacker with local code execution, malicious dependency, XSS in a dApp embedding the SDK, etc.).

### Likelihood Explanation
Medium: exploitation requires the attacker to obtain local read access to the storage medium (browser `localStorage`/IndexedDB origin access via XSS, or filesystem access on a Node host running the SDK). This is a real, commonly-achieved foothold class (analogous to the Artemis "local attacker reads shadow file" scenario), and the SDK provides no mitigation (no encryption, no OS keychain integration) — it is a design gap present in the shipped storage module, not a hypothetical misconfiguration.

### Recommendation
Encrypt `SessionKeyData.privateKey` at rest before calling `baseStorage.setItem`, using a key derived from a user-supplied passphrase, OS keychain/credential manager, or WebCrypto-protected key wrapped per session, so plaintext keys are never persisted. Alternatively, scope session keys to minimum-necessary lifetime/permissions (e.g., ensure they cannot authorize arbitrary solver addresses beyond the intended bid window) and document/require host applications to use secure storage backends. Consider zeroizing keys from memory/storage immediately after the `SelectSolver` signature has been produced and the order is finalized.

### Proof of Concept
1. A dApp or filler uses `createSessionKeyStorage()` and calls `setSessionKey(commitment, { privateKey, address, createdAt })` when creating an order's session key (as used from `OrderPlacer.ts`/`Bid.ts`).
2. In a browser environment, `detectEnvironment()` selects `localstorage`, and the key is written as plaintext JSON under `session-key:<commitment>` ( [8](#0-7) ).
3. An attacker with any script-execution primitive on the same origin (XSS, malicious embedded widget, browser extension) or, in Node, local filesystem read access to the SDK's data directory, reads this value directly — no decryption needed.
4. The attacker calls `CryptoUtils.signSolverSelection(commitment, attackerSolverAddress, domainSeparator, stolenPrivateKey)` and submits `IntentGatewayV2.select()` with the forged signature, diverting solver selection for that order to an address of their choosing ( [9](#0-8) ).

### Citations

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

**File:** sdk/packages/sdk/src/storage/index.ts (L220-264)
```typescript
export function createSessionKeyStorage(options: SessionKeyStorageOptions = {}) {
	const key = options.env ?? detectEnvironment()
	const driver = loadDriver({ key, options }) ?? inMemoryDriver()
	const baseStorage = createStorage({ driver })

	const SESSION_KEY_PREFIX = "session-key:"
	const SESSION_KEY_ADDRESS_PREFIX = "session-key-address:"

	/**
	 * Gets a session key by order commitment
	 */
	const getSessionKey = async (commitment: HexString): Promise<SessionKeyData | null> => {
		const storageKey = `${SESSION_KEY_PREFIX}${commitment}`
		const value = await baseStorage.getItem<string>(storageKey)
		if (!value) return null

		try {
			return JSON.parse(value) as SessionKeyData
		} catch {
			return null
		}
	}

	/**
	 * Gets a session key by session key address
	 */
	const getSessionKeyByAddress = async (address: HexString): Promise<SessionKeyData | null> => {
		const storageKey = `${SESSION_KEY_ADDRESS_PREFIX}${address.toLowerCase()}`
		const value = await baseStorage.getItem<string>(storageKey)
		if (!value) return null

		try {
			return JSON.parse(value) as SessionKeyData
		} catch {
			return null
		}
	}

	/**
	 * Stores a session key for an order commitment
	 */
	const setSessionKey = async (commitment: HexString, data: SessionKeyData): Promise<void> => {
		const storageKey = `${SESSION_KEY_PREFIX}${commitment}`
		await baseStorage.setItem(storageKey, JSON.stringify(data))
	}
```

**File:** sdk/packages/sdk/src/storage/load-driver.ts (L1-3)
```typescript
// Important: DO NOT REMOVE or RENAME this module
// Note: uses only Node driver during development.
export { loadDriver } from "./drivers/node"
```

**File:** sdk/packages/sdk/src/storage/types.ts (L1-13)
```typescript
import type { Driver } from "unstorage"

export type StorageDriverKey = "node" | "localstorage" | "indexeddb" | "memory"

export interface CancellationStorageOptions {
	env?: StorageDriverKey
	basePath?: string
}

export interface SessionKeyStorageOptions {
	env?: StorageDriverKey
	basePath?: string
}
```

**File:** sdk/packages/sdk/src/protocols/intents/Bid.ts (L102-166)
```typescript
	private async signSelection(): Promise<HexString> {
		if (this.cachedSignature) return this.cachedSignature

		const commitment = this.order.id as HexString
		const sessionKeyAddress = this.order.session as HexString

		const sessionKeyData = this.sessionPrivateKey
			? { privateKey: this.sessionPrivateKey }
			: await this.ctx.sessionKeyStorage.getSessionKeyByAddress(sessionKeyAddress)
		if (!sessionKeyData) {
			throw new Error(`SessionKey not found for commitment: ${commitment}`)
		}

		const signature = await CryptoUtils.signSolverSelection(
			commitment,
			this.solverAddress,
			this.domainSeparator,
			sessionKeyData.privateKey,
		)
		if (!signature) {
			throw new Error("Failed to sign solver selection")
		}

		this.cachedSignature = signature
		return signature
	}

	/**
	 * Simulates this bid on-chain by batching the `select` and `fillOrder` calls
	 * via `eth_call` from the solver's account, using the IntentGatewayV2 ERC-7821
	 * batch-execute pattern.
	 *
	 * The native value forwarded to the simulation is the sum of any native-token
	 * (`address(0)`) output amounts plus the Hyperbridge dispatch fee.
	 *
	 * @throws If the `eth_call` simulation reverts or errors.
	 */
	async simulate(): Promise<void> {
		const signature = await this.signSelection()

		const selectOptions: SelectOptions = {
			commitment: this.order.id as HexString,
			solver: this.solverAddress,
			signature,
		}

		// Compute the native ETH the fillOrder call requires:
		// native token outputs (address(0)) + Hyperbridge dispatch fee
		const nativeOutputs = this.fillOptions.outputs.reduce(
			(acc, o) => (bytes32ToBytes20(o.token) === ADDRESS_ZERO ? acc + o.amount : acc),
			0n,
		)
		const simulationValue = nativeOutputs + this.fillOptions.nativeDispatchFee

		const selectCalldata = encodeFunctionData({
			abi: IntentGatewayV2ABI,
			functionName: "select",
			args: [selectOptions],
		}) as HexString

		const calls: ERC7821Call[] = [
			{ target: this.intentGatewayV2Address, value: 0n, data: selectCalldata },
			{ target: this.solverAddress, value: simulationValue, data: this.userOp.callData },
		]
		const batchedCalldata = this.crypto.encodeERC7821Execute(calls)
```
