### Title
Protocol fee and surplus-share truncate to zero on small order amounts, letting solver/user avoid fee collection - (File: evm/src/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.placeOrder` computes the protocol fee taken from each input token with integer division by `10_000`, exactly the same truncation-prone pattern flagged in the referenced Surge `Pool.sol` interest bug (`numerator / constant_denominator`). When `originalAmount * protocolFeeBps < 10_000`, the fee rounds down to zero and the full amount is escrowed fee-free. The same pattern recurs in the solver-surplus split.

### Finding Description
The protocol fee is computed as:
```solidity
uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
``` [1](#0-0) 

At the currently documented default of 5 bps, any input whose base-unit amount times `protocolFeeBps` is below `10_000` (e.g. an input amount under 2,000 base units at 5 bps) computes `protocolFee == 0`, so `reducedAmount == originalAmount` and no `DustCollected` fee is ever taken — the `if (protocolFee > 0)` guard only gates the event, not the (already-zero) deduction. This is directly analogous to the reported `Pool.sol` bug where `_interest` truncates to 0 when `_totalDebt` is small relative to the fixed denominator.

The identical arithmetic shape recurs for the solver-surplus split:
```solidity
uint256 protocolShare = (surplus * SURPLUS_SHARE_BPS) / 10_000;
``` [2](#0-1) 
which is computed on-chain in the fill path with the same division and is subject to the same rounding-to-zero for small surplus amounts.

`placeOrder` is reachable by any unprivileged caller placing an intent order — the exact "intents escrow" surface explicitly in scope — with no floor enforced on `order.inputs[i].amount`, so a caller fully controls whether the multiplication clears the `10_000` denominator. [3](#0-2) [4](#0-3) 

### Impact Explanation
A user or solver can systematically split what would otherwise be one order with a nonzero fee into many sub-threshold orders, each computing `protocolFee = 0`. Repeated at scale, this becomes an unbounded way to route intent volume through the gateway while permanently denying the protocol its fee revenue on that volume — a direct, repeatable loss to the fee recipient (the gateway/treasury), mirroring the "loss to the fee recipient" impact called out in the source report. It is a systemic economic bypass rather than a one-off rounding error, since the division is deterministic and attacker-controlled via the freely chosen `order.inputs[i].amount`.

### Likelihood Explanation
Likelihood is high: any address can call `placeOrder` with an arbitrarily small input amount and a token of low enough decimals (or simply a small enough sub-unit amount) to force `originalAmount * protocolFeeBps < 10_000`, with no minimum-amount check anywhere in the fee-deduction path. Automating this against a live fee-bearing route costs only ordinary user gas and requires no special privileges.

### Recommendation
Enforce a minimum representable amount before applying the bps fee (revert or round up instead of down when `originalAmount * protocolFeeBps < 10_000`), or require `protocolFee > 0` whenever `protocolFeeBps > 0` and `originalAmount > 0`, reverting the order (similar to `PriceNotRepresentable()` in `BandwidthManager.purchase()`) rather than silently allowing a fee-free escrow. Apply the same fix to the `SURPLUS_SHARE_BPS` computation in the fill path.

### Proof of Concept
1. Deploy/observe `IntentGatewayV2` with `protocolFeeBps = 5` (current default per docs). [5](#0-4) 
2. Call `placeOrder` with `order.inputs[0].amount = 1000` (base units of the input token).
3. In the fee loop, `protocolFee = (1000 * 5) / 10_000 = 0`; `reducedAmount = 1000` unchanged, `DustCollected` never fires. [6](#0-5) 
4. Repeat the call N times (splitting a larger intended order into many ≤1999-unit chunks) to move arbitrary total volume through the gateway while the protocol collects 0 fee on every chunk, versus the intended `amount * 5 / 10_000` fee had it been placed as one order.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-196)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
        if (order.inputs.length == 0) revert InvalidInput();

```

**File:** evm/src/apps/IntentGatewayV2.sol (L228-236)
```text
        uint256 inputsLen = order.inputs.length;

        // Phase 1: Transfer tokens and record actual received amounts.
        // For fee-on-transfer tokens, the gateway receives less than the requested amount.
        // We mutate order.inputs to reflect actual received so the commitment and escrow
        // are consistent with what the gateway holds.
        uint256 msgValue = msg.value;
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;
```

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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L1562-1571)
```text
        // surplus = 100 DAI, 50% to beneficiary, 50% to protocol
        uint256 surplus = 100 * 1e18;
        uint256 beneficiaryShare = surplus - (surplus * SURPLUS_SHARE_BPS) / 10_000;
        assertEq(
            dai.balanceOf(user),
            userDaiBefore + outputAmount + beneficiaryShare,
            "User should receive output + beneficiary surplus share"
        );
        uint256 protocolShare = (surplus * SURPLUS_SHARE_BPS) / 10_000;
        assertEq(dai.balanceOf(address(intentGateway)), protocolShare, "Gateway should hold protocol surplus share");
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
