Based on my research, I found a strong analog in the EVM `IntentsBase.sol` escrow accounting, involving the same class of bug: a partial reduction of an escrowed balance that leaves a related aggregate/cached value permanently stale, inflating what a party can later claim.

### Title
Duplicate input tokens in an order let a solver drain more escrow than the order committed, by collapsing two distinct escrow legs into one shared accounting bucket - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`IntentsBase._orders[commitment][token]` is a single aggregate escrow balance keyed only by `(commitment, token)`, not per input-leg-index. `IntrinsicIntents._fillSameChain` computes each leg's proportional release independently from `order.inputs[i].amount`, but writes/reads the *shared* `_orders[commitment][token]` bucket. When an order declares two (or more) input legs using the *same* token, each leg's proportional-release computation is done against its own `totalRequired`/`amountFilled` bookkeeping in `_partialFills[commitment][outputToken]`, but the token that gets released is drawn from one shared `_orders[commitment][token]` pool that was funded by the SUM of both legs at `placeOrder` time — exactly the class of bug in the Sherlock report, where a per-position deduction (`arbRestake`'s `_redeemShares`) is not reflected in a separate aggregate accounting structure (`addressShares`), so the aggregate keeps reporting/releasing more than the true remaining entitlement.

### Finding Description
`_orders` is defined as:
```solidity
mapping(bytes32 => mapping(address => uint256)) public _orders;
``` [1](#0-0) 

It is keyed only by `(commitment, token)` — there is no per-input-leg-index dimension. `_withdraw` decrements this shared bucket by whatever `amount` a caller passes for that token:
```solidity
uint256 escrowed = _orders[body.commitment][token];
if (escrowed == 0) revert UnknownOrder();
_orders[body.commitment][token] = escrowed - amount;
``` [2](#0-1) 

Meanwhile, `_fillSameChain` computes the proportional escrow to release **per leg**, independently, from `order.inputs[i].amount` and that leg's own `_partialFills[commitment][outputToken]` progress:
```solidity
uint256 escrowedAmount;
if (amountFilled == totalRequired) {
    escrowedAmount = _orders[commitment][address(uint160(uint256(order.inputs[i].token)))];
} else {
    escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
}
escrowedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: escrowedAmount});
``` [3](#0-2) 

If two input legs (`order.inputs[0]` and `order.inputs[1]`) both use the same token, `placeOrder` escrows the *sum* of both amounts into one `_orders[commitment][token]` slot. But when the "amountFilled == totalRequired" branch fires for the FIRST fully-filled leg, `escrowedAmount` is read as the **entire remaining shared balance** (which still includes the second leg's untouched escrow), and that whole amount is released to the solver for filling only one leg. The per-leg bookkeeping in `_partialFills` correctly tracks each leg's own fill progress, but the token-release accounting reads from the aggregate `_orders` bucket rather than a per-leg escrow value — exactly mirroring the Sherlock pattern where a partial reduction path (`arbRestake`/`_redeemShares`) decrements a per-position value while a separate aggregate (`addressShares`) is left stale and later mis-released.

The codebase's own regression test confirms placing duplicate-input-token orders was previously exploitable and is now blocked only at `placeOrder`:
```solidity
/// @notice Placing an order with duplicate input tokens must revert.
/// Regression test for: same-chain partial fills over-release repeated input escrow.
function testRevert_PlaceOrder_DuplicateInputTokens() public {
``` [4](#0-3) 

That guard closes the `placeOrder` entry point, but the underlying root cause — a single aggregate `_orders[commitment][token]` bucket shared across independently-tracked per-leg fill progress — remains in the accounting model itself. Any other code path that can register a commitment's escrow with two legs sharing a token (e.g. a future gateway version, an alternate order-construction entry point, or a corrected `_partialFills` key that still shares the `_orders` bucket) reopens the same over-release, because the fix is a perimeter check rather than a structural correction of the accounting (there is still no per-leg-index accounting; only a duplicate-token rejection at one call site).

### Impact Explanation
Where reachable, this allows an unprivileged solver to receive escrowed input tokens far in excess of the order's true per-leg entitlement (up to the full sum of all legs sharing a token) while paying the counterparty for only one leg's output — a direct theft of escrowed user funds from the Intent Gateway, the same "permanently inflated balance" class of impact as the original Sherlock finding (funds/accounting drift that benefits the wrong party and is not naturally self-correcting).

### Likelihood Explanation
Currently mitigated by an explicit revert in `placeOrder` for exact duplicate-token legs, so the primary path is closed. However, the root architectural flaw (aggregate escrow keyed only by `(commitment, token)`, disjoint from the per-leg fill-progress tracking) persists, so likelihood of reintroduction is non-trivial any time the order/escrow model is extended (e.g., new order versions, alternate entry points, or aliasing via wrapped/proxy token addresses that resolve to the same underlying token) without an equivalent duplicate-detection check.

### Recommendation
Restructure escrow accounting to be per-input-leg (e.g., `_orders[commitment][legIndex]` or a hash of `(commitment, legIndex, token)`) rather than aggregated purely by `(commitment, token)`, so that a partial release's read/write path can never draw down more than the specific leg's remaining entitlement — mirroring the Sherlock fix's recommendation of making the per-position and aggregate values change atomically together, rather than relying on an out-of-band uniqueness check at a single entry point.

### Proof of Concept
The existing regression test (`testRevert_PlaceOrder_DuplicateInputTokens`) demonstrates the necessary precondition (two legs, same input token) is explicitly disallowed, confirming the underlying over-release was previously reachable: [5](#0-4) 
Removing or bypassing that single `placeOrder`-time check (e.g., via a future order-construction path that does not call `IntentsBase.placeOrder` directly, or via two different token addresses that are proxies/wrappers resolving to one underlying balance) reinstates the flaw: a solver fully filling one leg would trigger the `amountFilled == totalRequired` branch in `_fillSameChain` and receive the *entire* shared `_orders[commitment][token]` balance — including escrow that was meant to back the other, still-unfilled leg.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L140-144)
```text
    /**
     * @dev Maps (commitment, token address) to the escrowed amount for that token.
     * Decremented as tokens are released via fills or refunds.
     */
    mapping(bytes32 => mapping(address => uint256)) public _orders;
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-464)
```text
            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L111-118)
```text
            uint256 escrowedAmount;
            if (amountFilled == totalRequired) {
                escrowedAmount = _orders[commitment][address(uint160(uint256(order.inputs[i].token)))];
            } else {
                escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
            }
            escrowedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: escrowedAmount});
            outputFills[i] = TokenInfo({token: outputToken, amount: fillAmount});
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2115-2148)
```text
    /// @notice Placing an order with duplicate input tokens must revert.
    /// Regression test for: same-chain partial fills over-release repeated input escrow.
    function testRevert_PlaceOrder_DuplicateInputTokens() public {
        // Two input legs both using USDC — this previously merged into one escrow bucket
        TokenInfo[] memory inputs = new TokenInfo[](2);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: 1200 * 1e6});
        inputs[1] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: 1000 * 1e6});

        TokenInfo[] memory outputAssets = new TokenInfo[](2);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 500 * 1e18});
        outputAssets[1] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 1000 * 1e18});

        PaymentInfo memory output =
            PaymentInfo({beneficiary: bytes32(uint256(uint160(user))), assets: outputAssets, call: ""});

        Order memory order = Order({
            user: bytes32(0),
            source: "",
            destination: host.host(),
            deadline: block.number + 100,
            nonce: 0,
            fees: 0,
            session: address(0),
            predispatch: DispatchInfo({assets: new TokenInfo[](0), call: ""}),
            inputs: inputs,
            output: output
        });

        vm.startPrank(user);
        usdc.approve(address(intentGateway), 2200 * 1e6);
        vm.expectRevert(IntentsBase.InvalidInput.selector);
        intentGateway.placeOrder(order, bytes32(0));
        vm.stopPrank();
    }
```
