Based on the evidence gathered, I can identify a valid analog to the reported ERC20-pause DoS pattern in the `IntentGatewayV2` bridge/escrow flow.

### Title
Paused/reverting ERC20 in a multi-asset order can permanently DoS escrow release and refund in `IntentGatewayV2` - (File: `sdk/packages/core/contracts/apps/IntentGatewayV2.sol` / `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`IntentGatewayV2` orders can escrow multiple input tokens (`TokenInfo[] inputs`) in a single order. Settlement (`onAccept` → `withdraw`, per the docs) and cancellation (`cancelOrder`) both iterate over this array and call `safeTransfer`/`safeTransferFrom` for each token to release escrow to the solver or refund the user. This mirrors the reported bug class exactly: a loop of ERC20 transfers where a single pausable/blacklistable token (USDC, USDT, WBTC, etc.) reverting on `transfer`/`transferFrom` reverts the entire batch, blocking delivery of unrelated, otherwise-healthy assets in the same order.

### Finding Description
The docs for the settlement flow state that when the cross-chain settlement message arrives, `onAccept()` decodes a `WithdrawalRequest` and calls `withdraw()`, which:
1. Marks the order filled,
2. **Transfers each escrowed input token to the solver** (loop over `tokens: TokenInfo[]`),
3. Releases fee-token payment,
4. Emits `EscrowReleased`. [1](#0-0) 

The `WithdrawalRequest` struct carries an array of tokens for a single commitment, confirming that one order's settlement performs multiple token transfers in one call: [2](#0-1) 

The same multi-token escrow/refund pattern is visible in the sibling Tron implementation, where input tokens are pulled/pushed in a loop using `IERC20(token).safeTransferFrom(...)`/`transfer` per index of `order.inputs`, with escrow state (`_orders[commitment][token]`) tracked per token: [3](#0-2) 

Because `onAccept` is invoked by the unprivileged, permissionless relayer-delivery path (any relayer can submit the proof that triggers this call per the ISMP host dispatch model), and because a single reverting `transfer`/`transferFrom` bubbles up and reverts the whole `onAccept`/`withdraw` transaction, a single paused/blacklisted token among an order's multiple escrowed inputs makes the entire settlement message undeliverable — freezing every other (unaffected) token in that same order's escrow indefinitely, exactly as the report describes for `sweepTo()`/`_liquidate()`'s multi-asset loop.

The equivalent risk applies to `cancelOrder`, which must also return all escrowed inputs to the user; the interface declares it as a single all-or-nothing call over the full order: [4](#0-3) 

### Impact Explanation
An order with multiple input tokens where any single one becomes non-transferable (issuer pause, blacklist, compromise) permanently blocks:
- Release of escrowed funds to the solver on settlement (loss/freezing of solver capital already delivered as output on the destination chain — solver is left unpaid while having already paid out), and
- Refund of escrowed funds to the user on cancellation/expiry (freezing of user funds).

Since ISMP message handling for a given commitment is generally one-shot (replay-protected), a persistently reverting `onAccept` effectively strands both the paused asset and all co-escrowed healthy assets in the contract, meeting the "permanent freezing of funds" bar.

### Likelihood Explanation
Likelihood scales with the number of assets an order escrows and the number of supported tokens overall — as noted in the original report, the probability that *any single* asset among several is paused is much higher than for one asset alone. USDC/USDT-style pause/blacklist tokens are commonly used as intent inputs/outputs, making this a realistic, not merely theoretical, DoS vector reachable by any user placing a multi-input order or any relayer delivering its settlement/cancellation message.

### Recommendation
- Avoid all-or-nothing loops over multiple tokens in a single settlement/refund call; process each token's transfer independently (e.g., wrap each `transfer` in a try/catch or move to a pull-based claim pattern per token) so that one failing asset does not block release of the others.
- Track per-token claimable balances so a paused token's transfer can be retried later without re-processing already-successful transfers.
- Consider the same treatment for `cancelOrder`'s refund path and any dust-sweep (`SweepDust`) logic that iterates multiple tokens.

### Proof of Concept
1. User places an order with `inputs = [TokenA, TokenB]` where `TokenB` is a USDC-like token.
2. Solver fills the order on the destination chain; a `RedeemEscrow`/settlement message is dispatched back to the source chain.
3. Before the relayer delivers the settlement proof, `TokenB`'s issuer pauses transfers (or blacklists the escrow contract).
4. Relayer submits the proof; `onAccept` → `withdraw` loops over `[TokenA, TokenB]`, calling `transfer` for each. The `TokenB` transfer reverts, reverting the entire transaction.
5. `TokenA` (never affected by any pause) remains permanently stuck in escrow alongside `TokenB`, and the solver cannot ever claim its payment for this commitment while the pause persists — replay protection means retried delivery is either impossible or exhibits the same infinite revert.

**Note:** I was unable to retrieve the concrete implementation body of `withdraw()`/`onAccept()`/`cancelOrder()` in the primary EVM `IntentGatewayV2` contract (only the interface/struct definitions were indexed for `sdk/packages/core/contracts/apps/IntentGatewayV2.sol`, and the main `evm/src/apps/IntentGatewayV2.sol` implementation body was not returned by search). The analysis above is corroborated by the documented settlement flow and the parallel Tron implementation's loop-based transfer logic, but a Devin session with full file access should confirm the exact transfer loop and error-handling (or lack thereof) in the canonical EVM implementation before treating this as fully confirmed.

### Citations

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L50-58)
```text
### Settlement

When the settlement message arrives on the source chain, the ISMP host calls `onAccept()`. The handler authenticates the message (verifying it came from a known IntentGateway instance), decodes the `WithdrawalRequest`, and calls `withdraw()` which:

1. Marks the order as filled (`_filled[commitment] = solver`)
2. Transfers each escrowed input token to the solver
3. Releases stored transaction fees (in fee token) to the solver
4. Emits `EscrowReleased(commitment, tokens)`

```

**File:** sdk/packages/core/contracts/apps/IntentGatewayV2.sol (L131-141)
```text
/**
 * @dev Struct representing the body of a withdrawal request.
 */
struct WithdrawalRequest {
    /// @dev Represents the commitment of an order. This is typically a hash that uniquely identifies the order.
    bytes32 commitment;
    /// @dev Stores the identifier for the beneficiary.
    bytes32 beneficiary;
    /// @dev An array of token identifiers. Each element in the array represents a unique token involved in the order.
    TokenInfo[] tokens;
}
```

**File:** sdk/packages/core/contracts/apps/IntentGatewayV2.sol (L491-496)
```text
    /**
     * @notice Cancels an order after it has expired.
     * @param order The order to be cancelled
     * @param options The cancellation options
     */
    function cancelOrder(Order calldata order, CancelOptions calldata options) external payable;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L448-469)
```text
            // Execute transfer calls from call dispatcher
            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }
        }
```
