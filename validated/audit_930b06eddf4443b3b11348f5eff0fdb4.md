Based on my research, I found a concrete analog: the SDK's `createSessionKeyStorage` persists ephemeral order-authorization private keys unencrypted, in browser `localStorage`/`indexedDB`.

### Title
Order session-key private keys are persisted unencrypted in browser storage, letting any local process, XSS, or disk access hijack solver selection - ([File: sdk/packages/sdk/src/storage/index.ts])

### Summary
When a user places an order through `OrderPlacer.placeOrder`, the SDK generates a fresh ephemeral ECDSA "session key" and immediately writes its raw hex `privateKey` to persistent storage via `createSessionKeyStorage`/`setSessionKeyByAddress` [1](#0-0) . In a browser environment this storage resolves to plain `localStorage` or `indexedDB` with no encryption layer [2](#0-1) [3](#0-2) . This mirrors the reported bug class: sensitive signing-key material kept in cleartext where any code/process with access to the host (an XSS payload, a malicious browser extension, or a disk/backup inspection) can trivially exfiltrate it — analogous to the wallet mnemonic sitting unencrypted in process memory.

### Finding Description
`createSessionKeyStorage` stores `SessionKeyData` (containing `privateKey: HexString`) as a raw `JSON.stringify`'d blob under keys like `session-key-address:<address>`, with no encryption, hashing, or wrapping of the secret [4](#0-3) . The session key is not a throwaway artifact — it is the sole credential that authorizes which solver may fill a placed order: it signs the EIP-712 `SelectSolver` message consumed on-chain by `IntentGatewayV2._select` / `SolverAccount.validateUserOp`, which recovers the session key and stores an authorization for `fillOrder` to honor via `tstore` [5](#0-4) [6](#0-5) . Any party who reads this key out of `localStorage`/`indexedDB` (client-side JS via any XSS in an app embedding the SDK, a compromised browser extension, or offline inspection of browser profile data) can independently sign `SelectSolver` messages for the victim's outstanding orders and authorize an arbitrary attacker-controlled solver address to fill them.

### Impact Explanation
Session-key compromise lets an attacker author a valid solver-selection signature for the user's pending order and steer `fillOrder` authorization to a solver address the attacker controls, at any point up until the order deadline. Combined with a colluding/attacker-owned solver account, the escrowed input funds can be released to that attacker-chosen `msg.sender` rather than the solver the user actually intended, which is a fund-theft path directly reachable from a single unprivileged order placement — the exact "unprivileged token bridger/intent solver" surface called out in scope. No admin, governance, or infrastructure compromise is required — only host-level access to the browser storage, matching the report's "un-encrypted secret" bug class.

### Likelihood Explanation
Every call to `OrderPlacer.placeOrder` writes the raw private key to disk-backed storage for the lifetime of the order (until `removeSessionKeyByAddress` is called) [7](#0-6) . Any application embedding this SDK in a browser context (the common integration point for solving/order UIs) exposes this key to the same-origin JS execution context and to anything with local disk access — a low bar compared to remote consensus or contract-level attacks.

### Recommendation
Encrypt session-key private keys at rest (e.g., with a per-session-derived symmetric key, WebCrypto non-extractable keys, or requiring a user-supplied passphrase) before calling `baseStorage.setItem` in `createSessionKeyStorage`, and avoid ever materializing the raw key in a serializable JS object that outlives the signing operation. At minimum, scope the storage lifetime tightly and zero/remove the key immediately once the order is finalized or canceled.

### Proof of Concept
1. Use the SDK in a browser app to call `OrderPlacer.placeOrder(order)`.
2. Inspect browser `localStorage`/`indexedDB` (or run any injected script, e.g. via a stored XSS in a page sharing the origin) for the key `session-key-address:<address>` written by `setSessionKeyByAddress` [8](#0-7) .
3. Parse the JSON value to recover `privateKey`.
4. Independently call `CryptoUtils.signSolverSelection(commitment, attackerSolverAddress, domainSeparator, privateKey)` [9](#0-8)  to produce a valid `SelectSolver` signature authorizing the attacker's own `SolverAccount` to fill the victim's order, then submit it through `IntentGatewayV2.select`/`fillOrder` as demonstrated in the test harness [10](#0-9) .

### Citations

**File:** sdk/packages/sdk/src/protocols/intents/OrderPlacer.ts (L92-153)
```typescript
	async *placeOrder(
		order: Order,
		graffiti: HexString = DEFAULT_GRAFFITI,
	): AsyncGenerator<
		{ to: HexString; data: HexString; sessionPrivateKey: HexString },
		{ order: Order; receipt: TransactionReceipt },
		HexString
	> {
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

		const data = encodeFunctionData({
			abi: IntentGatewayV2ABI,
			functionName: "placeOrder",
			args: [transformOrderForContract(placementOrder), graffiti],
		}) as HexString

		const intentGatewayAddress = this.ctx.source.configService.getIntentGatewayAddress(
			normalizeStateMachineId(order.source),
		)

		const signedTransaction = yield {
			to: intentGatewayAddress,
			data,
			sessionPrivateKey: privateKey as HexString,
		}

		const receipt =
			signedTransaction.length === 66
				? await this.ctx.source.getTransactionReceipt(signedTransaction)
				: await this.ctx.source.broadcastTransaction(signedTransaction)

		const events = parseEventLogs({
			abi: IntentGatewayV2ABI,
			logs: receipt.logs,
			eventName: "OrderPlaced",
		})

		const orderPlacedEvent = events[0] as DecodedOrderPlacedLog | undefined
		if (!orderPlacedEvent) {
			throw new Error("OrderPlaced event not found in transaction receipt")
		}

		const finalizedOrder = deriveCanonicalPlacedOrder(placementOrder, orderPlacedEvent.args)

		const sessionKeyData: SessionKeyData = {
			privateKey: privateKey as HexString,
			address: sessionKeyAddress,
			commitment: finalizedOrder.id,
			createdAt,
		}

		await this.ctx.sessionKeyStorage.setSessionKeyByAddress(sessionKeyAddress, sessionKeyData)
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

**File:** sdk/packages/sdk/src/storage/index.ts (L220-272)
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

	/**
	 * Stores a session key for a session key address
	 */
	const setSessionKeyByAddress = async (address: HexString, data: SessionKeyData): Promise<void> => {
		const storageKey = `${SESSION_KEY_ADDRESS_PREFIX}${address.toLowerCase()}`
		await baseStorage.setItem(storageKey, JSON.stringify(data))
	}
```

**File:** sdk/packages/sdk/src/storage/drivers/browser.ts (L1-14)
```typescript
import indexedDBDriver from "unstorage/drivers/indexedb"
import localStorageDriver from "unstorage/drivers/localstorage"
import type { LoadDriver } from "../types"

const BASE_KEY = "hyperbridge/sdk/proof"

export const loadDriver: LoadDriver = ({ key }) => {
	if (key === "localstorage") {
		return localStorageDriver({ base: BASE_KEY })
	}

	if (key === "indexeddb") {
		return indexedDBDriver({ base: BASE_KEY })
	}
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L560-572)
```text
    function _select(SelectOptions calldata options) internal returns (address) {
        bytes32 structHash = keccak256(abi.encode(SELECT_SOLVER_TYPEHASH, options.commitment, options.solver));
        bytes32 digest = _hashTypedDataV4(structHash);
        address sessionKey = ECDSA.recover(digest, options.signature);

        bytes32 commitment = options.commitment;
        bytes32 selectionHash = keccak256(abi.encode(options.solver, sessionKey));
        assembly {
            tstore(commitment, selectionHash)
        }

        return sessionKey;
    }
```

**File:** evm/src/apps/intentsv2/SolverAccount.sol (L118-134)
```text
        bytes32 commitment = bytes32(op.signature[0:32]);
        bytes calldata solverSignature = op.signature[32:97];
        bytes calldata sessionSignature = op.signature[97:162];

        // Call IntentGatewayV2.select to recover the sessionKey. This also stages the
        // transient-storage selection that fillOrder enforces at execution.
        SelectOptions memory selectOptions =
            SelectOptions({commitment: commitment, solver: address(this), signature: sessionSignature});
        bytes memory selectCalldata = abi.encodeWithSelector(SELECT_SELECTOR, selectOptions);
        (bool success, bytes memory returnData) = INTENT_GATEWAY_V2.call(selectCalldata);

        if (!success || returnData.length < 32) return ERC4337Utils.SIG_VALIDATION_FAILED;

        address sessionKey = abi.decode(returnData, (address));
        uint192 userOpNonce = uint192(uint256(keccak256(abi.encodePacked(commitment, sessionKey))));
        if (uint192(op.nonce >> 64) != userOpNonce) return ERC4337Utils.SIG_VALIDATION_FAILED;
        if (!_rawSignatureValidation(userOpHash, solverSignature)) return ERC4337Utils.SIG_VALIDATION_FAILED;
```

**File:** sdk/packages/sdk/src/protocols/intents/CryptoUtils.ts (L105-124)
```typescript
	static async signSolverSelection(
		commitment: HexString,
		solverAddress: HexString,
		domainSeparator: HexString,
		privateKey: HexString,
	): Promise<HexString | null> {
		const account = privateKeyToAccount(privateKey as Hex)

		const structHash = keccak256(
			encodeAbiParameters(
				[{ type: "bytes32" }, { type: "bytes32" }, { type: "address" }],
				[SELECT_SOLVER_TYPEHASH, commitment, solverAddress],
			),
		)

		const digest = keccak256(concat(["0x1901" as Hex, domainSeparator as Hex, structHash]))
		const signature = await account.sign({ hash: digest })

		return signature as HexString
	}
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L1483-1527)
```text
    function testSelect() public {
        // Test solver selection with valid session signature
        uint256 inputAmount = 1000 * 1e6;

        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: inputAmount});

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 1000 * 1e18});

        PaymentInfo memory output =
            PaymentInfo({beneficiary: bytes32(uint256(uint160(user))), assets: outputAssets, call: ""});

        Order memory order = Order({
            user: bytes32(uint256(uint160(user))),
            source: host.host(),
            destination: host.host(),
            deadline: block.number + 1000,
            nonce: 0,
            fees: 0,
            session: vm.addr(1), // Session key
            predispatch: DispatchInfo({assets: new TokenInfo[](0), call: ""}),
            inputs: inputs,
            output: output
        });

        vm.startPrank(user);
        usdc.approve(address(intentGateway), inputAmount);
        intentGateway.placeOrder(order, bytes32(0));
        vm.stopPrank();

        bytes32 commitment = keccak256(abi.encode(order));

        // Create EIP-712 signature from session key
        bytes memory sessionSignature = _createSelectSolverSignature(
            commitment,
            filler,
            1, // Session key private key
            address(intentGateway)
        );

        // Solver selects themselves
        vm.prank(filler);
        intentGateway.select(SelectOptions({commitment: commitment, solver: filler, signature: sessionSignature}));
    }
```
