This confirms the analysis. The premise of the question — that padding "0xa" collides with a "completely different account" — is incorrect for Aptos/Movement's address model.

### Analysis

Aptos/Movement account addresses are fixed-size 32-byte values. Short hex literals like `0xa` and zero-padded forms like `0x000...00a` are simply two textual representations of the identical 32-byte account address — this is standard Move/Aptos VM address representation (e.g., framework addresses `0x1`, token addresses `0xa` are always written unpadded but are the same account as their zero-padded form). `validateMovementAddress` in `packages/intents-sdk/src/lib/validateAddress.ts` (lines 449-469) accepts short hex forms below 60 chars only when they pad out to a value matching `/^0{63}[0-9a-fA-F]$/` — i.e., a single hex nibble account, exactly matching Aptos's canonical special/short addresses.

Critically, `compareAddresses`'s `normalizeHexAddress` (`packages/intents-sdk/src/lib/compareAddresses.ts` lines 80-89) applies the *same* normalization philosophy — strip `0x`, lowercase, strip leading zeros — for `Chains.Aptos`, `Chains.Movement`, `Chains.Sui`, and `Chains.Starknet` together, explicitly documented: "both zero-padded (`0x000...01`) and short (`0x1`) forms refer to the same address" [1](#0-0) . This is verified by the existing spec: `compareAddresses("0xAB", "0x" + "0".repeat(60) + "00ab", Chains.Movement)` is asserted `true` [2](#0-1) , and `validateAddress("0xa", Chains.Movement)` / `validateAddress("a", Chains.Movement)` are both asserted `true` in the existing test suite [3](#0-2) .

So there is no divergence: the two "sides" the question asks to check — (1) the raw string address written into the withdrawal intent, and (2) the canonical padded form resolved on-chain — refer to the *same* Aptos/Movement account per the protocol's own address semantics, not two different accounts. `0xa` is not a "different address" from `0x000...00a`; it is the same address written with leading zeros elided, exactly analogous to how `0x01` and `0x1` are the same integer. There is no known Aptos/Movement wallet, explorer, or Move VM implementation that treats these two encodings as distinct accounts — the VM's `AccountAddress::from_hex_literal` and equivalent parsers zero-extend short hex literals to the full 32-byte representation before use. Downstream tooling does not "treat short and full forms differently" as the question assumes; this premise has no support in the repo or in Aptos's documented address format. [4](#0-3) [5](#0-4) 

#No vulnerability found for this question.

### Citations

**File:** packages/intents-sdk/src/lib/compareAddresses.ts (L12-68)
```typescript
export function compareAddresses(
	a: string,
	b: string,
	blockchain: Chain,
): boolean {
	try {
		switch (blockchain) {
			case Chains.Ethereum:
			case Chains.Optimism:
			case Chains.BNB:
			case Chains.Gnosis:
			case Chains.Polygon:
			case Chains.Monad:
			case Chains.LayerX:
			case Chains.Adi:
			case Chains.Base:
			case Chains.Arbitrum:
			case Chains.Avalanche:
			case Chains.Berachain:
			case Chains.Plasma:
			case Chains.Scroll:
			case Chains.Abstract:
			case Chains.HyperCore:
			case Chains.HyperEvm:
				return getAddress(a) === getAddress(b);
			case Chains.Aptos:
			case Chains.Movement:
			case Chains.Sui:
			case Chains.Starknet:
				return compareHexAddress(a, b);
			case Chains.TON:
				return compareTonAddress(a, b);
			case Chains.Tron:
				return compareTronAddress(a, b);
			case Chains.Stellar:
				return a.toUpperCase() === b.toUpperCase();
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
			default:
				blockchain satisfies never;
				return false;
		}
	} catch {
		return false;
	}
}
```

**File:** packages/intents-sdk/src/lib/compareAddresses.ts (L70-78)
```typescript
// Aptos/Movement/Sui/Starknet addresses are hex field elements: case is not
// significant, and both zero-padded (0x000...01) and short (0x1) forms refer
// to the same address.
function compareHexAddress(a: string, b: string): boolean {
	const normalizedA = normalizeHexAddress(a);
	const normalizedB = normalizeHexAddress(b);
	if (normalizedA === null || normalizedB === null) return false;
	return normalizedA === normalizedB;
}
```

**File:** packages/intents-sdk/src/lib/compareAddresses.spec.ts (L36-44)
```typescript
	it.each([Chains.Aptos, Chains.Movement, Chains.Sui, Chains.Starknet])(
		"compares %s addresses ignoring case and leading zeros",
		(chain) => {
			const short = "0xAB";
			const padded = `0x${"0".repeat(60)}00ab`;
			expect(compareAddresses(short, padded, chain)).toBe(true);
			expect(compareAddresses(short, "0xac", chain)).toBe(false);
		},
	);
```

**File:** packages/intents-sdk/src/lib/validateAddress.spec.ts (L580-596)
```typescript
describe("validateMovementAddress", () => {
	it("accepts valid Movement addresses", () => {
		expect(
			validateAddress(
				"0xbc3557a52bcac15d470e6ffa421eeea105baffd8471d6aa2c0238380f363ccd3",
				Chains.Movement,
			),
		).toBe(true);
		expect(validateAddress("0xa", Chains.Movement)).toBe(true);
		expect(validateAddress("a", Chains.Movement)).toBe(true);
		expect(
			validateAddress(
				"bc3557a52bcac15d470e6ffa421eeea105baffd8471d6aa2c0238380f363ccd",
				Chains.Movement,
			),
		).toBe(true);
	});
```

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L448-469)
```typescript
// Accept non strict addresses
function validateMovementAddress(address: string) {
	let parsedAddress = address;
	if (address.startsWith("0x")) {
		parsedAddress = address.slice(2);
	}

	if (parsedAddress.length === 0 || parsedAddress.length > 64) {
		return false;
	}

	if (!/^[a-fA-F0-9]+$/.test(parsedAddress)) {
		return false;
	}

	if (parsedAddress.length >= 60) {
		return true;
	}

	const paddedAddress = parsedAddress.padStart(64, "0");
	return /^0{63}[0-9a-fA-F]$/.test(paddedAddress);
}
```
