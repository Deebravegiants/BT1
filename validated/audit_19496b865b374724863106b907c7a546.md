Based on my research, I found the direct analog to the reported bug class in `IntentGatewayV2.placeOrder`.

### Title
Protocol fee rounds down to zero for small-value order inputs, letting placed orders skip the fee entirely - (File: `evm/src/apps/IntentGatewayV2.sol`)

### Summary
`placeOrder`'s fee computation mirrors the AAVE `calculateLoanOriginationFee` rounding bug: it computes `protocolFee = (originalAmount * protocolFeeBps) / 10_000` and only *conditionally* emits `DustCollected` when the result is non-zero, but never validates that the fee itself is non-zero before proceeding. Any `originalAmount` small enough that `originalAmount * protocolFeeBps < 10_000` yields `protocolFee == 0`, silently waiving the protocol fee for that input.

### Finding Description
In `_placeOrder` (reachable by any unprivileged caller via `placeOrder`), the protocol fee for each escrowed input is computed as: [1](#0-0) 
```solidity
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
        ...
```
This is the same integer-division truncation pattern as the AAVE `FeeProvider.calculateLoanOriginationFee` bug: for any `originalAmount < 10_000 / protocolFeeBps`, `protocolFee` truncates to `0`, and `reducedAmount == originalAmount` — the order is placed with **zero** protocol fee deducted, and no error/revert occurs; only the `DustCollected` event is skipped. The same pattern also appears in `_splitSurplus` (`IntentsBase.sol`), used at fill time for surplus-sharing: [2](#0-1) 
```solidity
function _splitSurplus(uint256 dust, bool hasOutputCall)
    internal
    view
    returns (uint256 protocolShare, uint256 beneficiaryShare)
{
    if (hasOutputCall) return (dust, 0);
    protocolShare = (dust * _params.surplusShareBps) / 10_000;
    beneficiaryShare = dust - protocolShare;
}
```
For small surplus amounts relative to `surplusShareBps`, `protocolShare` truncates to zero and the entire surplus goes to the beneficiary, bypassing the protocol's configured cut with no revert or floor check.

Per the documentation, deployments currently configure `protocolFeeBps` as low as 5 bps (0.05%): [3](#0-2) 

meaning the zero-fee threshold is `10_000 / 5 = 2_000` raw token units — i.e. every input amount below 2,000 raw units (in the token's smallest denomination) pays no protocol fee whatsoever, with no revert to signal the anomaly.

### Impact Explanation
This lets a caller place cross-chain or same-chain intent orders that entirely bypass the protocol fee for sufficiently small per-input amounts, or (via `_splitSurplus`) capture 100% of a small surplus that should be partially retained by the protocol. This matches the impact class in the source report: unpaid fees represent leaked protocol revenue that governance/treasury is entitled to via `DustCollected`/`SweepDust`.

### Likelihood Explanation
The threshold amount that triggers zero fee (raw token units, not decimal-adjusted) is small in absolute terms for common ERC-20 decimals (e.g. below 2,000 raw units for USDC's 6 decimals is ~$0.002), so any single order exploiting this nets negligible value, and repeated exploitation is bounded by gas costs per `placeOrder`/`fillOrder` call exceeding the fee saved. Likelihood of this being economically worthwhile at scale is low, but the code path is reachable by any unprivileged user on every `placeOrder`/`fillOrder` call and the missing revert-on-zero-fee is a direct, provable defect matching the reported bug class.

### Recommendation
Mirror the fix referenced in the report (MR#75): revert `placeOrder`/`_splitSurplus` (or the equivalent path) when `protocolFeeBps > 0` (or `surplusShareBps > 0`) but the computed fee/share rounds to zero for a non-zero input/dust amount, e.g. `if (protocolFee == 0) revert FeeTooSmall();`. Alternatively, document explicitly that inputs below `10_000 / protocolFeeBps` raw units are fee-exempt by design, and add unit tests asserting this boundary behavior (as the AAVE report also recommended).

### Proof of Concept
1. Governance sets `protocolFeeBps = 5` (matches documented production default).
2. A user calls `placeOrder` with `order.inputs[0].amount = 1999` (raw units) for any ERC-20 token.
3. `protocolFee = (1999 * 5) / 10_000 = 0` (integer division truncates `0.9995` to `0`).
4. `reducedAmount = 1999 - 0 = 1999`; no `DustCollected` event fires; the full amount is escrowed with zero protocol fee collected, and the call succeeds without reverting.
5. Repeating this with many small-value inputs (or applying the analogous `_splitSurplus` path with `surplusShareBps` and small surplus amounts on `fillOrder`) systematically avoids fee collection that governance expects to be collected on every fee-bearing order/fill.

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L426-434)
```text
    function _splitSurplus(uint256 dust, bool hasOutputCall)
        internal
        view
        returns (uint256 protocolShare, uint256 beneficiaryShare)
    {
        if (hasOutputCall) return (dust, 0);
        protocolShare = (dust * _params.surplusShareBps) / 10_000;
        beneficiaryShare = dust - protocolShare;
    }
```

**File:** docs/content/developers/evm/intent-gateway/placing-orders.mdx (L94-111)
```text
### Protocol fees

Before escrowing, the contract deducts a protocol fee from each input amount:

```
protocolFee = input.amount × protocolFeeBps / 10_000
reducedAmount = input.amount − protocolFee
```

The fee is retained in the gateway as dust (emitting `DustCollected`), and per-destination overrides take precedence over the global `protocolFeeBps` when set. Current deployments charge **5 bps (0.05%)**. For a 100 USDC input:

| Item | Amount |
| --- | ---: |
| USDC transferred from your wallet | 100.000000 USDC |
| Protocol fee: `100 × 5 / 10,000` | 0.050000 USDC |
| Amount actually escrowed and offered to solvers | 99.950000 USDC |

The commitment hash is computed over the **fee-reduced inputs** — solvers read the reduced amounts from the `OrderPlaced` event and only need to match those. The fee is deducted at placement and is **not refunded** if the order expires, receives no bids, or is cancelled; a cancellation returns the remaining escrow and `order.fees`, but not the protocol fee.
```
