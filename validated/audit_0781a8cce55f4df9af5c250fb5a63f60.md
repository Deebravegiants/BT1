### Title
`validateStellarAddress` accepts G-addresses with invalid CRC16 checksum, allowing Stellar `destinationAddress` values that Stellar itself would reject - (`packages/intents-sdk/src/lib/validateAddress.ts`)

### Summary
`validateStellarAddress` only checks the address shape with `/^G[A-Z0-9]{55}$/` and never decodes/verifies the base32 payload's CRC16-XModem checksum that Stellar's StrKey format requires. This lets an attacker-supplied `destinationAddress` pass `validateAddress`/SDK validation while being an address that Stellar nodes/wallets would reject as malformed, breaking the equality "validated address == payable address" that every other chain validator in this file enforces (Bitcoin, Tron, Litecoin, Dash, TON, Aleo, BCH all verify checksums; Stellar does not).

### Finding Description
`validateAddress(address, Chains.Stellar)` dispatches to: [1](#0-0) 
which calls: [2](#0-1) 

This is a pure regex check on the character set and length. Stellar's actual StrKey encoding is base32 (RFC4648, alphabet `A-Z2-7`, not `A-Z0-9`) over `[version byte][32-byte payload][2-byte CRC16-XModem checksum]`. The current regex both (a) accepts characters (`0`,`1`,`8`,`9`) that are not even part of Stellar's base32 alphabet, and (b) performs no checksum verification of any kind — unlike the sibling validators in the same file, e.g. `validateBtcBase58Address` (SHA256d checksum), `validateTronBase58Address` (SHA256d checksum), `validateDashAddress` (SHA256d checksum), `validateLitecoinBase58Address` (SHA256d checksum), and `validateTonAddress`/`validateAleoAddress` (bech32/CRC checks) at lines 140-158, 384-403, 801-831, 537-567, 414-434, and 758-799 respectively.

The broken equality: `validateStellarAddress(addr) === true` should imply "Stellar's StrKey decoder accepts `addr` as a well-formed, checksum-valid public key." After this check, that equality does not hold — any 57-char string starting with `G` and using `[A-Z0-9]` characters passes, regardless of whether the CRC16 bytes are correct.

Exploit flow: an attacker (counterparty/integrator-forwarded string, e.g. a quote counterpart supplying their own Stellar `destinationAddress`) submits a G-address whose last 1-2 base32 characters are flipped from a valid address, corrupting only the trailing CRC16 checksum bytes while keeping the 32-byte payload intact-looking. `validateStellarAddress` returns `true` because the regex only checks shape.

### Impact Explanation
If SDK/integrator logic treats `validateAddress(...) === true` as sufficient proof that a Stellar destination is well-formed and safe to route funds to, a withdrawal could be constructed toward a checksum-invalid address. Whether this actually reaches an irrecoverable on-chain payment depends on downstream behavior: Stellar-side infrastructure (horizon/RPC or the bridge itself) would very likely reject a checksum-invalid StrKey during its own decode step before submitting a payment operation, since Stellar's SDKs always re-verify the checksum when parsing a `G...` address. I could not fully trace the Stellar withdrawal submission path in the `poa-bridge`/other bridge modules within the tool budget available, so I cannot confirm with certainty that this specific SDK-level gap has no downstream backstop. Given the rules require rejecting findings that rely on "trust assumptions about external RPCs/bridge APIs" providing the actual safety net, and given Stellar's own address parsers universally re-validate the checksum, the practical exploitable path to fund loss is not established purely from this regex weakness — the guard that matters (Stellar's own StrKey decode) sits outside this repo, is expected to reject the malformed address, and the question requires demonstrating this SDK gap alone causes an irrecoverable misroute, which is not shown.

### Likelihood Explanation
Trivial to construct a proof string that satisfies the regex but fails CRC16 (attacker cost near zero, fully repeatable). However exploitability of actual fund loss is gated by whether any code downstream of this SDK-level format check submits the payment to Stellar without Stellar's own checksum validation kicking in first — a dependency on external infra (out of scope per the rules) rather than a defect purely within this repo's reachable code path.

### Recommendation
`validateStellarAddress` should decode the StrKey manually (or via a vetted Stellar SDK's key-decoding utility) and verify: (1) the alphabet is restricted to RFC4648 base32 `A-Z2-7`, (2) the version byte corresponds to `ED25519_PUBLIC_KEY` (`G`), and (3) the trailing 2-byte CRC16-XModem checksum matches the computed checksum over version+payload, mirroring the checksum verification pattern already used for Bitcoin/Tron/Litecoin/Dash/TON in this same file.

### Proof of Concept
```ts
import { describe, expect, it } from "vitest";
import { validateAddress } from "./validateAddress";
import { Chains } from "./caip2";

describe("validateStellarAddress checksum gap", () => {
	it("accepts a G-address with a corrupted CRC16 checksum", () => {
		// Take a real, valid Stellar G-address and flip its last character,
		// which lies within the trailing CRC16 checksum bytes of the StrKey encoding.
		const valid = "GAXQC6TWRKQ4TK7OVADU2DQMXHFYUDHGO6JIIIHLDD7RTBHYHXPSNUTV";
		const corruptedChecksum = `${valid.slice(0, -1)}${valid.at(-1) === "V" ? "W" : "V"}`;

		// Both sides of the claimed equality:
		// LHS: SDK's validateAddress result
		// RHS: what a correct Stellar StrKey decoder (with CRC16 check) would report
		expect(validateAddress(corruptedChecksum, Chains.Stellar)).toBe(true); // LHS: passes (bug)
		// RHS would be `false` under a real StrKey decode+CRC16 verification —
		// demonstrating validateStellarAddress diverges from Stellar's own address acceptance.
	});
});
```

**Note on scope/confidence**: this finding demonstrates a genuine format-validation gap in `validateStellarAddress` relative to Stellar's StrKey spec, matching the question's proof idea exactly. However, per the audit rules excluding "trust assumptions about external RPCs/bridge APIs," I was unable to confirm within this repo's reachable code that this gap alone (absent any external Stellar-side re-validation) results in an irrecoverable fund misroute — Stellar's own address decoders are expected to re-check the CRC16 checksum before any payment is submitted. This should be verified against the actual Stellar submission path (e.g., inside the bridge that ultimately builds/submits the Stellar transaction) to confirm whether this repo submits payments without relying on that external check.

### Citations

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L62-63)
```typescript
		case Chains.Stellar:
			return validateStellarAddress(address);
```

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L440-442)
```typescript
function validateStellarAddress(address: string) {
	return /^G[A-Z0-9]{55}$/.test(address);
}
```
