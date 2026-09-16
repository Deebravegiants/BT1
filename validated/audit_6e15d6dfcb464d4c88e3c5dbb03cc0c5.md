### Title
Protocol fee rounds down to zero for low-value or low-decimal token inputs in `IntentGatewayV2.placeOrder` - (File: evm/src/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2` (and its Tron/SDK mirrors) computes the protocol fee taken from an order's input tokens using integer division: `protocolFee = (originalAmount * protocolFeeBps) / 10_000`. When `originalAmount * protocolFeeBps < 10_000`, the fee truncates to zero, and the protocol collects nothing on that input, exactly the rounding-loss bug class described in the reference report (fee computed as `matchAmount * feePercentage / denominator` truncating to 0 for low-decimal/low-value amounts).

### Finding Description
In `placeOrder`, once actual received amounts are known, the contract computes the protocol fee per input token: [1](#0-0) 

```solidity
if (protocolFeeBps > 0) {
    reducedInputs = new TokenInfo[](inputsLen);
    for (uint256 i; i < inputsLen;) {
        uint256 originalAmount = order.inputs[i].amount;
        if (originalAmount == 0) revert InvalidInput();
        uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
        uint256 reducedAmount = originalAmount - protocolFee;
        ...
        if (protocolFee > 0) emit DustCollected(token, protocolFee);
        reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
```

`protocolFeeBps` is governance-configured (e.g. 5–100 bps per the docs, `docs/content/developers/evm/intent-gateway/placing-orders.mdx:99`), and the calculation is plain integer division with a fixed `10_000` denominator with no minimum-amount check and no rounding-up. The identical pattern exists in the Tron deployment: [2](#0-1) 

and is mirrored in the SDK's fee-quoting helper, which explicitly documents the floor behavior: [3](#0-2) 

Any user calling `placeOrder` with a token whose smallest unit represents high value relative to decimals (e.g., a 0–2 decimal stablecoin, or wrapped BTC-style tokens with 8 decimals combined with a low `protocolFeeBps` such as 5 bps used in current deployments), or simply a small enough `originalAmount`, can cause `originalAmount * protocolFeeBps / 10_000` to floor to `0`. In that case `protocolFee == 0`, no `DustCollected` event fires, and `reducedAmount == originalAmount` — the full amount proceeds to escrow with zero protocol fee collected. Because there's no per-order minimum-fee enforcement or amount validation preventing "fee-free" order sizes, an actor can systematically split larger amounts into many small orders (or simply repeatedly use tokens/amounts below the rounding threshold) to bridge/settle value while permanently avoiding the protocol fee that governance intended to charge on every order.

### Impact Explanation
This causes the protocol to permanently lose fee revenue it is entitled to under its own fee configuration — a direct value-leakage bug reachable from a single unprivileged `placeOrder` call, and exploitable repeatedly/systematically by any solver-order flow that keeps `originalAmount * protocolFeeBps` below `10_000`. This is a protocol-owned funds loss (missed fee accrual), matching the severity class of the referenced report (protocol losing out on fees for low-decimal/low-value tokens due to floor-division truncation).

### Likelihood Explanation
Likelihood is high for tokens with few decimals (e.g., USDC-like 6-decimal tokens used with the smallest configured fee tiers, or any token with ≤2–6 decimals) and for any attacker deliberately structuring orders (many small orders instead of one large order) to zero out the fee on each. No special privileges are required — this is triggerable by any caller of `placeOrder` on any EVM (and Tron) deployment of `IntentGatewayV2` with `protocolFeeBps > 0`.

### Recommendation
Either (a) round the fee calculation up (`divCeil`) so any non-zero `protocolFeeBps` always yields `protocolFee >= 1` wei when `originalAmount > 0`, or (b) enforce a minimum order/input amount per token such that `originalAmount * protocolFeeBps / 10_000` cannot floor to zero, or (c) accumulate fractional-fee remainders across orders per token so they aren't silently lost. The SDK's `grossUpForProtocolFee`/`divCeil` helpers already demonstrate the rounding-up approach used for quoting and could be mirrored on-chain for fee collection.

### Proof of Concept
1. Deploy `IntentGatewayV2` with `protocolFeeBps = 5` (5 bps, the documented current default per `docs/content/developers/evm/intent-gateway/placing-orders.mdx:103`).
2. Place an order with an ERC20 input token of `originalAmount` such that `originalAmount * 5 < 10_000`, e.g. `originalAmount = 1999` (any token unit, e.g. a low-decimal token or dust-sized input): `1999 * 5 / 10_000 = 0`.
3. Observe: `protocolFee == 0`, no `DustCollected` event emitted, `reducedAmount == originalAmount == 1999`, and the full amount is escrowed for the solver with zero fee retained by the gateway.
4. Repeat with many such small-amount orders (or use a low-decimal token where typical order sizes fall under this threshold) to move economically significant total value through the gateway while the protocol collects no fee at all.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L340-356)
```text
        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                if (originalAmount == 0) revert InvalidInput();
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
                }
            }

```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L359-374)
```text
        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                // Emit DustCollected for protocol fee if non-zero
                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
                }
            }
```

**File:** sdk/packages/sdk/src/protocols/intents/quote/shared.ts (L45-50)
```typescript
/** Mirrors the gateway's floored fee deduction. */
export function deductProtocolFee(amount: bigint, protocolFeeBps: bigint): bigint {
	if (protocolFeeBps <= 0n) return amount
	const fee = (amount * protocolFeeBps) / BPS_DENOMINATOR
	return amount - fee
}
```
