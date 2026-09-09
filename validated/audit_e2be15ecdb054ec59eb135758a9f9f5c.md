### Title
DestinationAddressMatchesTokenAddressError bypass via "bitcoincash:" prefix mismatch between `compareAddresses` and `createWithdrawMemo` - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.validateWithdrawal` guards against withdrawing to a BCH token's own contract address by calling `compareAddresses(tokenInfo.origin_chain_address, args.destinationAddress, Chains.BitcoinCash)`, which for `Chains.BitcoinCash` does raw string equality `a === b` with no CashAddr-prefix normalization. `createWithdrawIntentPrimitive` → `createWithdrawMemo`, however, strips any `"bitcoincash:"` prefix (via `.toLowerCase().startsWith(...)`) before encoding the memo actually paid out. This lets a caller add a `"bitcoincash:"` prefix to `destinationAddress` to defeat the equality check while the memo still resolves to the bare token address.

### Finding Description
The claimed equality is: the string checked by `compareAddresses` in `validateWithdrawal` must equal the string actually encoded into the withdrawal memo by `createWithdrawMemo`.

- `compareAddresses` (`packages/intents-sdk/src/lib/compareAddresses.ts:48-60`) for `Chains.BitcoinCash` falls into the `a === b` branch — no lowercase normalization and no `"bitcoincash:"` prefix stripping.
- `createWithdrawMemo` (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts:28-49`) always does `receiverAddress.toLowerCase().startsWith("bitcoincash:")` before stripping the prefix. Because it lowercases the *entire string* first, this check correctly detects and strips the prefix for **any** casing variant (`bitcoincash:`, `BitcoinCash:`, `BITCOINCASH:`, etc.). So the question's specific premise — that a mixed-case prefix variant escapes this `.toLowerCase().startsWith()` logic — is incorrect; every casing of the prefix is stripped identically.
- The actual divergence is broader than casing: `compareAddresses`'s BCH branch performs **no prefix stripping at all**, in any case. If `tokenInfo.origin_chain_address` (from the POA bridge's `getSupportedTokens` API) is returned as a bare CashAddr payload (no `bitcoincash:` prefix — consistent with `createWithdrawMemo` producing bare addresses for the on-chain payout), then any `destinationAddress` submitted with a `"bitcoincash:"` prefix (lowercase or any other case) will fail `compareAddresses`'s `a === b` test even though it is the exact same address once `createWithdrawIntentPrimitive`/`createWithdrawMemo` strips the prefix for the memo that actually pays out.
- `validateAddress` (`packages/intents-sdk/src/lib/validateAddress.ts:214-269`, `validateBchCashAddr`) already lowercases and prefix-normalizes before validating format, so a prefixed, mixed-case address passes the format check at `poa-bridge.ts:181-188` without issue — nothing earlier in `validateWithdrawal` rejects a prefixed address.
- Exploit input: attacker sets `destinationAddress = "bitcoincash:" + <bare CashAddr equal to tokenInfo.origin_chain_address>` (any casing of the literal prefix). `validateAddress` passes it. `compareAddresses(tokenInfo.origin_chain_address, destinationAddress, Chains.BitcoinCash)` returns `false` (strings differ because of the prefix), so `DestinationAddressMatchesTokenAddressError` is never thrown. Later, `createWithdrawIntentPrimitive` → `createWithdrawMemo` strips the prefix, producing a memo whose address equals `tokenInfo.origin_chain_address` exactly — the withdrawal proceeds to the token's own contract address.

### Impact Explanation
The withdrawal intent (`ft_withdraw`, memo `WITHDRAW_TO:<address>`) that gets signed and submitted encodes a destination address identical to the token contract's own on-chain address, even though `validateWithdrawal`'s guard was specifically designed to reject exactly this case (`DestinationAddressMatchesTokenAddressError`). This matches the "Critical" category: funds are delivered to a wrong/self-referential address with no recovery path, since the guard meant to prevent it is bypassed. This is repeatable for every BCH-routed withdrawal on any token whose `origin_chain_address` is a bare CashAddr.

### Likelihood Explanation
Preconditions: the asset must route through `PoaBridge` and resolve to `Chains.BitcoinCash`, and `tokenInfo.origin_chain_address` returned by the bridge API must be a bare CashAddr (no prefix) — consistent with the address format `createWithdrawMemo` normalizes to for the actual payout. The attacker needs only to prepend `"bitcoincash:"` (in any case) to a valid destination address string they control — a trivial, zero-cost, fully client-side manipulation requiring no special privileges, available to any ordinary caller of `validateWithdrawal`/the withdrawal flow.

### Recommendation
Normalize CashAddr inputs in `compareAddresses`'s `Chains.BitcoinCash` branch the same way `createWithdrawMemo` does (lowercase, strip an optional `"bitcoincash:"` prefix from both sides) before doing the equality check, so the address compared is guaranteed to match the address ultimately encoded into the memo.

### Proof of Concept
```ts
import { describe, it, expect } from "vitest";
import { compareAddresses } from "../../lib/compareAddresses";
import { Chains } from "../../lib/caip2";

describe("BCH prefix bypass", () => {
  it("compareAddresses treats prefixed and bare CashAddr as different (bug)", () => {
    const bare = "qpm2qsllhun6ba1lq5g5m2s2v0y3rz2yh8s6ycgz3d"; // token's origin_chain_address
    const prefixed = "BitcoinCash:" + bare; // attacker-supplied destinationAddress
    // Equality claimed broken: validated string (compareAddresses) vs memo-encoded string
    expect(compareAddresses(bare, prefixed, Chains.BitcoinCash)).toBe(false); // guard misses the match
  });
});
```
And, mocking the POA bridge HTTP client's `getSupportedTokens` to return `origin_chain_address: bare`, call `PoaBridge.validateWithdrawal({ assetId, amount, destinationAddress: prefixed })` and assert it does **not** throw `DestinationAddressMatchesTokenAddressError`, while separately asserting `createWithdrawIntentPrimitive({ destinationAddress: prefixed, ... }).memo` ends with `:${bare}` — proving the validated string and the encoded string diverge.