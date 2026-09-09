## Analysis Result

The MoinMoin bug class (privilege gained by an identity that *looks* equal to a privileged one but isn't recognized as such by the check) has a genuine analog here: an **address-equality check that is bypassed because it does not canonicalize case-insensitive address encodings** before comparing.

### Title
Case-sensitive address comparison lets a withdrawal bypass the "destination == token's own address" guard for Bech32/CashAddr chains - (File: `packages/intents-sdk/src/lib/compareAddresses.ts`)

### Summary
`compareAddresses()` is the equality check every bridge uses to block a withdrawal whose destination address is actually the bridged token's own on-chain address (self-transfer to the token contract, which is unrecoverable). For Bitcoin, Litecoin, Cardano and Bitcoin Cash, it falls back to raw `a === b` string equality, but the address encodings for these chains (Bech32/Bech32m per BIP-173, and CashAddr) are explicitly **case-insensitive** — a valid address can be submitted entirely upper-cased and still decode to the identical underlying bytes. `validateAddress()` correctly accepts either case via `bech32.decode`/CashAddr normalization, but `compareAddresses()` never normalizes case before the strict string comparison. [1](#0-0) 

### Finding Description
`compareAddresses` dispatches per-chain: EVM chains use `getAddress()` (checksum-normalized), TON/Tron/hex-chains use dedicated decoders that normalize encoding, but `Chains.Near, Bitcoin, BitcoinCash, Zcash, Dogecoin, Litecoin, Solana, Fogo, XRPL, Cardano, Aleo, Dash` all share one branch that does plain `a === b`. [2](#0-1) [1](#0-0) 

For Bitcoin, `validateAddress()`'s Bech32 path decodes with `bech32.decode` / `bech32m.decode`, which per BIP-173 accept an all-uppercase address as valid and equivalent to its lowercase form: [3](#0-2) 

The same applies to Litecoin's Bech32 branch and Cardano's Bech32 branch, and to Bitcoin Cash's CashAddr, which the validator explicitly lower-cases before checking: [4](#0-3) [5](#0-4) 

Every bridge's `validateWithdrawal()` relies on `compareAddresses()` as the sole guard preventing a withdrawal from being routed to the bridged token's own custody/contract address (an unrecoverable, address-with-no-owner destination). Concretely, `PoaBridge.validateWithdrawal()`: [6](#0-5) 

and `OmniBridge.validateWithdrawal()`: [7](#0-6) 

and `HotBridge.validateWithdrawal()`: [8](#0-7) 

all pass the token's canonical address (`tokenInfo.origin_chain_address`, `destTokenAddress`, or the parsed asset's `address` — sourced from bridge APIs/indexers, typically in one fixed case) together with the caller-supplied `destinationAddress` into `compareAddresses`. If the caller supplies the token's own Bitcoin/Litecoin/Cardano/BCH address in a *different but valid case* than the stored canonical form, `validateAddress()` accepts the format, but `compareAddresses()`'s strict `===` fails to detect that it is the same underlying address, so `DestinationAddressMatchesTokenAddressError` is never thrown.

### Impact Explanation
The equality this breaks is: *"the destination address paid is not the token's own custody address that was validated against."* Bypassing it lets a withdrawal intent be constructed that sends funds to the bridged token's own contract/reserve address on-chain. This is exactly the "funds delivered to a wrong address/chain/contract with no recovery" impact class — such self-transfers to a token/bridge-controlled address are typically unrecoverable by the sender.

### Likelihood Explanation
Any caller of the SDK (or any integrator building a withdrawal UI on top of it) that accepts a raw, case-varied Bech32/CashAddr destination address (e.g. a QR code, address book entry, or user paste in a non-canonical case — all of which are valid per BIP-173/CashAddr spec) will silently pass this guard, and there is no other check in `createWithdrawalIntents`/`validateWithdrawal` that re-derives or canonicalizes the address before comparison.

### Recommendation
Canonicalize both operands before comparison in the `Bitcoin`, `BitcoinCash`, `Litecoin`, and `Cardano` branches of `compareAddresses` (e.g., decode via `bech32`/`bech32m`/CashAddr decoding and compare the resulting witness/payload bytes, mirroring what is already done for `TON` and `Tron`), instead of relying on raw string equality.

### Proof of Concept
1. A bridge's token has canonical Bitcoin Bech32 address `bc1qxyzexampletokenaddress...` (as returned by the bridge's supported-tokens/indexer API, stored lowercase).
2. Caller requests a withdrawal with `destinationAddress = "BC1QXYZEXAMPLETOKENADDRESS..."` (identical address, all uppercase — valid per BIP-173).
3. `validateAddress(destinationAddress, Chains.Bitcoin)` → `validateBtcBech32Address` decodes successfully → returns `true`.
4. `compareAddresses(tokenAddress, destinationAddress, Chains.Bitcoin)` hits the `Chains.Bitcoin` case, does `a === b` on the differently-cased strings → returns `false`.
5. `DestinationAddressMatchesTokenAddressError` is not thrown; `createWithdrawalIntents` proceeds to build a withdrawal to the token's own address. [6](#0-5) [1](#0-0)

### Citations

**File:** packages/intents-sdk/src/lib/compareAddresses.ts (L12-17)
```typescript
export function compareAddresses(
	a: string,
	b: string,
	blockchain: Chain,
): boolean {
	try {
```

**File:** packages/intents-sdk/src/lib/compareAddresses.ts (L48-60)
```typescript
			case Chains.Near:
			case Chains.Bitcoin:
			case Chains.BitcoinCash:
			case Chains.Zcash:
			case Chains.Dogecoin:
			case Chains.Litecoin:
			case Chains.Solana:
			case Chains.Fogo:
			case Chains.XRPL:
			case Chains.Cardano:
			case Chains.Aleo:
			case Chains.Dash:
				return a === b;
```

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L160-202)
```typescript
function validateBtcBech32Address(address: string): boolean {
	let decoded: { prefix: string; words: number[] };
	let isBech32m = false;

	try {
		decoded = bech32.decode(address as `${string}1${string}`);
	} catch {
		try {
			decoded = bech32m.decode(address as `${string}1${string}`);
			isBech32m = true;
		} catch {
			return false;
		}
	}

	if (decoded.prefix.toLowerCase() !== "bc") return false;

	const { words } = decoded;
	if (!words || words.length < 1) return false;

	const witnessVersion = words[0];
	if (witnessVersion === undefined || witnessVersion < 0 || witnessVersion > 16)
		return false;

	const program = bech32.fromWords(words.slice(1));
	const progLen = program.length;

	if (progLen < 2 || progLen > 40) return false;

	// v0: Bech32 only — 20 bytes (P2WPKH) or 32 bytes (P2WSH)
	if (witnessVersion === 0) {
		if (isBech32m) return false;
		return progLen === 20 || progLen === 32;
	}

	// v1: Bech32m only — 32 bytes (P2TR / Taproot)
	if (witnessVersion === 1) {
		if (!isBech32m) return false;
		return progLen === 32;
	}

	return false;
}
```

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L231-243)
```typescript
function validateBchCashAddr(address: string): boolean {
	// Normalize the address
	let normalized = address.toLowerCase();

	// Add prefix if missing
	if (!normalized.includes(":")) {
		normalized = `bitcoincash:${normalized}`;
	}

	// Must start with bitcoincash:
	if (!normalized.startsWith("bitcoincash:")) {
		return false;
	}
```

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L475-495)
```typescript
export function validateCardanoAddress(address: string) {
	try {
		// max length big enough for any Cardano Bech32 addr
		const { prefix, words } = bech32.decode(
			address as `${string}1${string}`,
			120,
		);

		// only mainnet
		if (prefix !== "addr") return false;

		// convert 5-bit words back to bytes
		const data = bech32.fromWords(words);
		//@ts-expect-error
		const addrType = data[0] >> 4;

		return addrType >= 0 && addrType <= 7;
	} catch {
		return false;
	}
}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L207-219)
```typescript
		if (
			tokenInfo.origin_chain_address !== "native" &&
			compareAddresses(
				tokenInfo.origin_chain_address,
				args.destinationAddress,
				assetInfo.blockchain,
			)
		) {
			throw new DestinationAddressMatchesTokenAddressError(
				tokenInfo.origin_chain_address,
				args.assetId,
			);
		}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L384-396)
```typescript
		const destTokenAddress = getAddress(destTokenOmniAddress);
		if (
			compareAddresses(
				destTokenAddress,
				args.destinationAddress,
				assetInfo.blockchain,
			)
		) {
			throw new DestinationAddressMatchesTokenAddressError(
				destTokenAddress,
				args.assetId,
			);
		}
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L277-284)
```typescript
		const nativeAsset = "native" in assetInfo;
		const token = nativeAsset ? "native" : assetInfo.address;
		if (
			!nativeAsset &&
			compareAddresses(token, args.destinationAddress, assetInfo.blockchain)
		) {
			throw new DestinationAddressMatchesTokenAddressError(token, args.assetId);
		}
```
