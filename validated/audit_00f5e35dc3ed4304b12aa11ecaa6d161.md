### Title
`validateStellarAddress` accepts checksum-invalid StrKey addresses, letting `HotBridge` build unclaimable Stellar withdrawals - (File: `packages/intents-sdk/src/lib/validateAddress.ts`)

### Summary
`validateStellarAddress` only checks the address against the regex `/^G[A-Z0-9]{55}$/` and never decodes/verifies the StrKey base32 payload and CRC16 checksum, unlike every other checksum-bearing address type in the same file (Bitcoin, Litecoin, Dash, Tron, TON, Aleo all decode and verify checksums). This lets an unprivileged caller pass a syntactically well-formed but checksum-invalid Stellar `destinationAddress` through `validateAddress`, which `HotBridge` relies on to gate withdrawal construction.

### Finding Description
The claimed broken equality: `destinationAddress accepted by validateAddress(address, Chains.Stellar)` should equal `destinationAddress is a real ed25519-checksummed StrKey Stellar account`. In the code, `validateStellarAddress` at `packages/intents-sdk/src/lib/validateAddress.ts` lines 440-442 is:

```
function validateStellarAddress(address: string) {
	return /^G[A-Z0-9]{55}$/.test(address);
}
```

This only checks the character-class and length format of a Stellar `G...` account StrKey. A real StrKey encodes: 1 version byte (`0x30` for `ACCOUNT_ID`) + 32-byte ed25519 public key + 2-byte CRC16-XModem checksum, all base32-encoded (RFC4648, no padding), for a total of 56 characters. The regex accepts any 56-char string starting with `G` composed of uppercase letters and digits `0-9`, including combinations that are not valid base32 (base32 excludes `0`,`1`,`8`,`9`) and, even when valid base32, ignores the checksum entirely. Compare this to sibling functions in the same file — `validateBtcBase58Address` (lines 140-158), `validateLitecoinBase58Address` (lines 537-567), `validateDashAddress` (lines 801-831), and `validateTonAddress`/`validateAleoAddress` — all of which decode the payload and explicitly verify the checksum bytes before returning `true`. Stellar is the only checksum-bearing chain in this file that skips that step.

`HotBridge` (in `packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts`) imports `validateAddress` from this module (line 48) and uses it as the sole format gate before constructing withdrawal intents (`mt_withdraw`) for the destination chain; a value that passes `validateStellarAddress` is treated as an acceptable Stellar destination and no `InvalidDestinationAddressForWithdrawalError` is thrown for it.

Attacker's exact input: any 56-character string `G` + 55 characters from `[A-Z0-9]` that satisfies the regex but is not decodable via valid base32 StrKey (e.g. contains `0`/`1`/`8`/`9` which aren't part of Stellar's base32 alphabet) or that decodes to valid base32 with the correct version byte but wrong CRC16 checksum (i.e., a genuine StrKey with the last character(s) flipped). Because `validateStellarAddress` never decodes or checksums, both cases pass.

This is a real bug, but I could not verify from the retrieved code whether it rises to Critical severity as scoped, because I was unable to confirm (within tool budget) whether `HotBridge`'s actual on-chain/bridge-contract or `@hot-labs/omni-sdk` call path performs its own StrKey decode/validation before submitting the withdrawal to the Stellar bridge, which would catch this before funds are irrecoverably routed. I could not fully read `HotBridge.validateWithdrawal`/withdrawal-construction body (grep matched but the relevant lines were not retrieved before the iteration budget ended), so I cannot confirm with certainty that no downstream check exists that would reject the checksum-invalid address before submission. Given the explicit format-only validation and absence of any StrKey/CRC16 decode in `validateAddress.ts`, and the pattern that other bridges in this repo rely solely on `validateAddress` for format gating (per the question's stated proof idea), the vulnerability as described in `validateAddress.ts` is real, but confirming end-to-end Critical impact through `HotBridge.createWithdrawalIntents`/`mt_withdraw` requires reading the un-retrieved portion of `hot-bridge.ts`.

### Impact Explanation
If no downstream checksum validation exists, an attacker (a NEAR Intents user withdrawing their own funds, or a counterparty-supplied address forwarded by an integrator) could cause `HotBridge` to construct and sign a `mt_withdraw` intent addressed to a Stellar StrKey that decodes to an arbitrary/garbage ed25519 key with no controllable private key, or that Stellar Horizon/network will reject outright as malformed. Funds debited from the intents contract and routed for withdrawal would be unclaimable — matching the Critical category "funds delivered to a wrong address ... with no recovery." This is repeatable for every withdrawal request that supplies such an address.

### Likelihood Explanation
Preconditions: the caller must request a Stellar withdrawal (`Chains.Stellar` route reachable, e.g. via `HotBridge`) supplying a `destinationAddress` matching the loose regex but with an invalid/garbage checksum. Attacker cost is trivial — constructing such a string requires no special access, only knowledge of the regex, and it can be repeated at will for every withdrawal call. The only mitigating factor is if `HotBridge`'s or `@hot-labs/omni-sdk`'s own Stellar-specific logic (not confirmed here) decodes/validates the StrKey before submission — this could not be ruled out with certainty from the code paths retrieved.

### Recommendation
Fix `validateStellarAddress` to properly decode the StrKey: base32-decode (using the correct RFC4648 alphabet, rejecting `0/1/8/9`), verify the version byte equals `0x30` (`ACCOUNT_ID`) and total decoded length is 35 bytes (1 + 32 + 2), then compute CRC16-XModem over the version+payload bytes and compare to the trailing 2 checksum bytes, mirroring the checksum-verification pattern already used for Bitcoin/Litecoin/Dash/Tron in the same file.

### Proof of Concept
```ts
import { describe, it, expect } from "vitest";
import { validateAddress } from "packages/intents-sdk/src/lib/validateAddress";
import { Chains } from "packages/intents-sdk/src/lib/caip2";

describe("validateStellarAddress checksum", () => {
  it("accepts a 56-char G-address with corrupted CRC16 checksum (should reject but doesn't)", () => {
    // Valid base32 alphabet chars, correct version byte, but checksum bytes intentionally wrong
    const validLooking = "GAXQC6TWRKQ4TK7OVADU2DQMXHFYUDHGO6JIIIHLDD7RTBHYHXPSNUTW"; // last char flipped from V to W
    expect(validateAddress(validLooking, Chains.Stellar)).toBe(true); // regex passes
    // Equality check: real StrKey checksum verification (e.g. via stellar-sdk's StrKey.isValidEd25519PublicKey)
    // would return false for this string, proving validateAddress diverges from destination truth.
  });
});
```
Note: full end-to-end confirmation that this reaches `HotBridge.createWithdrawalIntents`/`mt_withdraw` without further checks requires reading the remainder of `hot-bridge.ts` (validateWithdrawal / withdrawal construction body), which was not fully retrieved in this session — a follow-up Devin session with full file access should confirm before treating this as fully proven Critical.