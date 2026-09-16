## Analysis

This report's bug class (changing a token address without accounting for funds still locked in the old token) has a direct, reachable analog in `IntentGatewayV2` / `IntentsBase` on the EVM side of Hyperbridge's intents system.

### Root cause

`EvmHost.updateHostParamsInternal` only guards the *host's own* balance of the old `feeToken` before it lets governance swap it — it checks the host contract's own balance, not any downstream app's balance: [1](#0-0) 

`IntentGatewayV2.placeOrder` collects `order.fees` in whatever `feeToken()` the host reports *at placement time*, and escrows it under a fixed sentinel key that carries no reference to which token was actually collected: [2](#0-1) [3](#0-2) 

Later, when the order is finalized (fill, cross-chain redeem, refund, or cancel), `_withdraw` re-reads `feeToken()` from the host **at redemption time** and tries to pay out the escrowed fee amount in *that* token: [4](#0-3) 

If governance swaps `feeToken` on the host between `placeOrder` and finalization (which the host permits as long as the host's own balance of the old token is zero — a condition that says nothing about `IntentGatewayV2`'s escrow), the accounting under `TRANSACTION_FEES` no longer corresponds to any real balance the gateway holds:
- The gateway still holds the *old* feeToken funds (unreachable, since the sentinel record doesn't track which token they are in).
- `_withdraw` attempts `IERC20(newFeeToken).safeTransfer(...)`, which either transfers unrelated new-feeToken balance out to the wrong beneficiary/amount context, or reverts (`ERC20InsufficientBalance`) if the gateway holds none of the new token — and because the fee payout is bundled in the same atomic `_withdraw` call as the release of the escrowed input/output tokens, that revert blocks the entire order finalization, permanently freezing the user's/solver's principal escrow along with the stranded fee.

### Title
Cross-chain fee-token swap on `EvmHost` strands and can permanently lock escrowed order funds in `IntentGatewayV2` — ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentGatewayV2` escrows solver/relayer fees in whatever `IDispatcher(host).feeToken()` returns at `placeOrder` time, but records the escrowed amount under a token-agnostic sentinel key (`TRANSACTION_FEES`). `_withdraw` (used by `fillOrder`, cross-chain `RedeemEscrow`/`RefundEscrow` `onAccept` handling, and `cancelOrder`) re-resolves `feeToken()` at finalization time. `EvmHost.updateHostParamsInternal` only checks the *host's* own balance before allowing a `feeToken` change, not any app's escrowed balance, so governance can legitimately (or even routinely, e.g. after a Uniswap-routed native-fee-token swap) change the fee token while `IntentGatewayV2` still holds outstanding fee balances denominated in the old token.

### Finding Description
1. A user calls `placeOrder` with `order.fees > 0`. `IntentGatewayV2` pulls `order.fees` in the current `feeToken` (`evm/src/apps/IntentGatewayV2.sol:375-392`) and stores the amount at `_orders[commitment][TRANSACTION_FEES]` — a fixed address constant, not the actual token address used.
2. Before the order is filled/redeemed/cancelled, Hyperbridge governance calls `EvmHost.updateHostParams` to change `feeToken` (allowed as long as the *host's* balance of the old token is zero — `evm/src/core/EvmHost.sol:617-621`). `IntentGatewayV2`'s escrowed balance of the old fee token is entirely separate and unchecked.
3. When the order is later finalized via `_withdraw` (`evm/src/apps/intentsv2/IntentsBase.sol:451-485`), the code does `IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees)` using the *new* fee token address, while the actual funds held by the gateway are in the *old* fee token.
4. Because this transfer is inside the same atomic function that also releases the principal escrowed input/output tokens, a revert (insufficient balance in the new token) blocks the whole finalization — freezing not just the fee but the user's/solver's entire escrowed principal for that order.

### Impact Explanation
This is a permanent freezing-of-funds bug reachable from ordinary, unprivileged user flow (`placeOrder` → later `fillOrder`/cross-chain redeem/refund/cancel). Any order with `fees > 0` that straddles a `feeToken` update on the host becomes unfinalizable, locking the solver's fee and the principal escrow for both the user and the solver. This matches the "permanent freezing of funds" impact class.

### Likelihood Explanation
`feeToken` rotation is a documented, expected admin/governance operation on `EvmHost` (there's even a Uniswap-swap path baked into the fee-collection logic itself, and the codebase's own bandwidth-manager docs note "the host occasionally swaps fee tokens"). Any order placed shortly before such a rotation, with a nonzero relayer/solver fee, and finalized afterward, triggers the bug — no attacker action is required, only ordinary timing between order placement and settlement, and only requires the host's *own* balance of the old token (not the app's) to reach zero.

### Recommendation
Record the actual fee token address alongside (or in place of) the current fee amount when escrowing at `placeOrder` (e.g., `_orders[commitment][feeTokenAtPlacement]` or a parallel mapping), and use that stored token — not the live `feeToken()` — when paying out fees in `_withdraw`. Alternatively, require `EvmHost.updateHostParamsInternal` to also verify zero balances (or a drain) across all registered/known app escrow accounts before permitting a `feeToken` change, though the app-local fix is the more robust and general solution since it does not depend on governance knowing every downstream integrator's balance.

### Proof of Concept
1. User calls `IntentGatewayV2.placeOrder` with `order.fees = X`, feeToken == `TokenA`. Gateway pulls `X` `TokenA` from the user and sets `_orders[commitment][TRANSACTION_FEES] = X`.
2. Hyperbridge governance calls `EvmHost.updateHostParams` setting `feeToken = TokenB` (permitted since `EvmHost`'s own `TokenA` balance is 0 — it never held the app's escrow).
3. Solver fills the order; `fillOrder`/cross-chain settlement eventually calls `_withdraw(..., finalize: true)`.
4. `_withdraw` executes `IERC20(TokenB).safeTransfer(beneficiary, X)`, but the gateway holds `X` of `TokenA`, not `TokenB` — the call reverts (or, if the gateway happens to hold unrelated `TokenB` balance, misappropriates it), reverting the whole finalize call and leaving the user's/solver's principal escrow (`_orders[commitment][inputToken]`) permanently stuck since `_filled[commitment]` never gets set and the order can't be finalized again.

### Citations

**File:** evm/src/core/EvmHost.sol (L617-621)
```text
        address oldFeeToken = feeToken();
        if (oldFeeToken != address(0) && oldFeeToken != params.feeToken) {
            uint256 balance = IERC20(oldFeeToken).balanceOf(address(this));
            if (balance != 0) revert CannotChangeFeeToken();
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L61-66)
```text
    /**
     * @dev Sentinel address used as the key for storing Hyperbridge relayer fees
     * in the `_orders` mapping. Derived from keccak256("txFees") to avoid
     * collisions with real token addresses.
     */
    address internal constant TRANSACTION_FEES = address(uint160(uint256(keccak256("txFees"))));
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-485)
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

        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
            }

            if (isRefund) {
                emit EscrowRefunded({commitment: body.commitment, tokens: body.tokens});
            } else {
                emit EscrowReleased({commitment: body.commitment, tokens: body.tokens});
            }
        }
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L375-392)
```text
        if (order.fees > 0) {
            address feeToken = IDispatcher(hostAddr).feeToken();
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = feeToken;
                uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                    order.fees, path, address(this), block.timestamp
                );
                msgValue -= amounts[0];
            } else {
                IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
            }

            _orders[commitment][TRANSACTION_FEES] = order.fees;
        }
```
