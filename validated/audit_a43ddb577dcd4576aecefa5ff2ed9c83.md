Confirmed: `_withdraw` in `IntentsBase.sol` transfers a fixed recorded `escrowed` amount from `_orders[commitment][token]` via `IERC20(token).safeTransfer(beneficiary, amount)`, not the contract's live balance. [1](#0-0) 

### Title
Rebasing ERC20 input tokens held in IntentGatewayV2 escrow can be withdrawn inaccurately, causing fund loss or DoS on fills/refunds - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`IntentGatewayV2.placeOrder` correctly measures actual received token amounts via balance-diffing to defend against fee-on-transfer tokens at deposit time [2](#0-1) . However, the escrowed amount recorded in `_orders[commitment][token]` is a static snapshot fixed at deposit time [3](#0-2) . Whenever tokens are later released — on fill (`RedeemEscrow`), refund (`RefundEscrow`/`_cancelSameChain`) — `_withdraw` transfers exactly this recorded `escrowed` amount regardless of what the gateway's actual on-chain balance is at that time [4](#0-3) .

### Finding Description
The gateway's design assumes the balance of an escrowed ERC20 token remains static between `placeOrder` and the eventual `_withdraw` call. For a rebasing token (elastic-supply token whose `balanceOf` changes automatically over time, e.g., stETH-style rebasing or auto-compounding wrapped tokens), this assumption breaks: the recorded `_orders[commitment][token]` amount can diverge from the actual token balance the gateway holds by the time the order is filled, cancelled, or refunded (which for cross-chain orders can take an arbitrary length of time, spanning source dispatch, Hyperbridge relaying, and destination settlement round trips) [5](#0-4) .

This mirrors the exact bug class in the referenced Harpie report: a "logged"/recorded balance (`amountStored`) is used for withdrawal instead of the live, potentially-rebased balance, producing an accounting mismatch between recorded escrow and real custody.

### Impact Explanation
- If the rebasing token's supply increases (positive rebase) while escrowed, the recipient (solver on fill, or user on cancel/refund) only receives the stale, smaller recorded amount; the surplus is permanently stranded in the contract with no accounting path to recover it (it is not tracked as protocol dust, unlike the deliberate fee-on-transfer dust mechanism).
- If the rebasing token's supply decreases (negative rebase) while escrowed, the actual gateway balance can fall below the recorded `escrowed` amount. `IERC20(token).safeTransfer(beneficiary, amount)` in `_withdraw` will revert due to insufficient balance [6](#0-5) , permanently freezing the order: it can never be filled (transfer reverts), and cancellation/refund of the same escrow entry will also revert for the same reason, since `_withdraw` is the single code path used by all three release routes (fill, same-chain cancel, cross-chain refund).
- This is a concrete case of both fund loss (positive rebase, surplus stuck) and permanent freezing of funds (negative rebase, all release paths revert), meeting the bar for Medium/High severity.

### Likelihood Explanation
This is reachable by any unprivileged user simply calling `placeOrder` with a rebasing ERC20 as an input token — no special privileges, governance, or malicious actors required. The intent-gateway design does not appear to blocklist rebasing tokens; the only protective mechanism implemented (balance-diffing) targets transfer-time fee deduction, not post-deposit balance drift. Likelihood depends on whether the deployed governance/token-listing process permits rebasing tokens as valid `order.inputs`, but nothing in the contract logic itself prevents such a token from being used, and the escrow duration for cross-chain orders (bridging round-trip time) increases the window during which a rebase could occur.

### Recommendation
For each token released via `_withdraw`, either:
1. Track escrow as a proportional share of the gateway's per-token balance rather than an absolute snapshot amount, recomputing amount owed at release time from the live `balanceOf`, or
2. Explicitly disallow known-rebasing ERC20 tokens from being used as `order.inputs` (e.g., via an allowlist/denylist enforced at `placeOrder`), and clearly document this limitation, consistent with how many other bridging/escrow protocols handle rebasing tokens.

### Proof of Concept
1. User calls `placeOrder` with `order.inputs[0]` = 1000 units of a rebasing token `RBT`; `IntentGatewayV2` measures actual received (1000) and stores `_orders[commitment][RBT] = 1000` [3](#0-2) .
2. Before the order is filled/cancelled, `RBT` undergoes a negative rebase such that the gateway's actual `RBT.balanceOf(gateway)` drops to 950 (all holders' balances scaled down uniformly).
3. A solver calls `fillOrder`, which eventually invokes `_withdraw` with `amount = 1000` for `RBT`. `IERC20(RBT).safeTransfer(beneficiary, 1000)` reverts because the gateway only holds 950 [6](#0-5) .
4. The user then attempts `cancelOrder` to reclaim escrow; `_cancelSameChain`/cross-chain refund path also calls `_withdraw` with the same stale `escrowed = 1000`, which reverts identically — the order is permanently stuck with no way to release the escrow.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-470)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L312-328)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }

                unchecked {
                    ++i;
                }
            }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L364-373)
```text
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            // Reject duplicate input tokens
            if (_orders[commitment][token] != 0) revert InvalidInput();
            _orders[commitment][token] = reducedInputs[i].amount;

            unchecked {
                ++i;
            }
        }
```

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L50-58)
```text
### Settlement

When the settlement message arrives on the source chain, the ISMP host calls `onAccept()`. The handler authenticates the message (verifying it came from a known IntentGateway instance), decodes the `WithdrawalRequest`, and calls `withdraw()` which:

1. Marks the order as filled (`_filled[commitment] = solver`)
2. Transfers each escrowed input token to the solver
3. Releases stored transaction fees (in fee token) to the solver
4. Emits `EscrowReleased(commitment, tokens)`

```
