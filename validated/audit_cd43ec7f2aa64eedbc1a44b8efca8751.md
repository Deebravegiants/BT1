### Title
Escrowed input tokens accounted by fixed amount, not live balance, permanently locking rebasing-token yield - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentGatewayV2`/`IntentsBase` escrow tracks each order's input tokens by a fixed `uint256` amount in `_orders[commitment][token]`, credited once in `placeOrder` and only ever decremented in `_withdraw`. If a rebasing ERC-20 (e.g. an aToken-style token) is used as an order input, any balance increase that accrues to the gateway contract while the order sits in escrow is never reflected in `_orders`, is never released to the user (refund), solver (fill), or protocol (sweep), and becomes permanently stuck.

### Finding Description
`placeOrder` credits escrow with a snapshot amount taken at deposit time: [1](#0-0) 

The gateway does already defend against fee-on-transfer tokens by measuring `balanceOf` before/after the transfer and using the actually-received amount: [2](#0-1) 

But this only captures the balance delta at the moment of the `safeTransferFrom` call. It does not, and cannot, account for further balance growth that happens afterward due to a rebase — the escrowed amount recorded in `_orders[commitment][token]` is a static `uint256`, not a live, proportional claim on the contract's actual token balance.

Release paths (`fillOrder` → cross-chain redeem, `cancelOrder` → refund) transfer out exactly the escrowed amount and decrement it by that same amount: [3](#0-2) 

There is no mechanism analogous to the C4 "Cally" finding's recommended pro-rata tracking: nothing computes "current contract balance of token X minus sum of all currently-escrowed amounts for token X" to identify and release rebase-derived surplus. The `_sweepDust`/`SweepDust` path exists, but it is fed only by explicitly emitted `DustCollected` events (protocol fee cuts, fee-on-transfer measured at deposit, and CallDispatcher residuals) — it has no way to discover or account for token balance growth that occurs to already-escrowed funds after `placeOrder` completes: [4](#0-3) 

Consequently, once a rebasing token is placed as an order input, if the token rebases upward before the order is filled/refunded, the surplus balance sitting in the `IntentGatewayV2` contract has no owner: it is not part of any user's escrow (`_orders` sums are unchanged), not part of protocol dust (no `DustCollected` was ever emitted for it), and no governance action exists to claim it. This is functionally identical to the referenced Cally vulnerability where `vault.tokenIdOrAmount` is a fixed snapshot that never reflects rebase-driven balance growth, and rewards remain locked forever.

### Impact Explanation
This is a permanent freezing-of-funds bug (Medium severity per the same classification as the referenced Cally finding): any rebasing token accepted as an intent order input token will have its rebase yield trapped in the `IntentGatewayV2` contract indefinitely, benefiting neither the order placer, the solver, nor the protocol. Because `IntentGatewayV2` accepts arbitrary ERC-20 addresses as input tokens (no allow-list is visible in `placeOrder`), any user can create this condition by simply placing an order with a rebasing token, and the yield accrued during the (often multi-block, cross-chain) window between `placeOrder` and fill/refund is unrecoverable.

### Likelihood Explanation
Likelihood is limited to deployments/order flows that actually accept rebasing ERC-20s (e.g. aTokens, stETH-style tokens) as order inputs; standard tokens (USDC, DAI, wrapped native assets) are unaffected. Given `placeOrder` takes an arbitrary `token` address per `TokenInfo` with no on-chain restriction to a vetted asset list, and cross-chain orders can remain unfilled for extended windows awaiting relaying/proof delivery, exposure is plausible wherever token acceptance is permissionless.

### Recommendation
Either explicitly disallow known-rebasing tokens (e.g. via a governance-controlled allow-list already implied by the `TokenGovernor`-style asset registration used elsewhere in the codebase), or track escrow as a share of total pooled balance per token and allow excess balance (current `balanceOf(this)` minus sum of live `_orders` entries for that token) to be swept via a permissioned `SweepDust`-style pathway so that yield does not become permanently unclaimable.

### Proof of Concept
1. Deploy `IntentGatewayV2` and register a rebasing ERC-20 `R` (positive-rebase, e.g. increases every holder's `balanceOf` over time) with no special-casing.
2. User calls `placeOrder` with `order.inputs[0] = {token: R, amount: 1000}`. Contract measures `balBefore`/`balAfter` and credits `_orders[commitment][R] = 1000` per [2](#0-1) , and Phase 3 escrow credit [1](#0-0) .
3. Time passes; token `R` rebases, and `R.balanceOf(address(IntentGatewayV2))` grows to, say, 1050 (the extra 50 accrues automatically to all holders, including the gateway).
4. Order is filled or cancelled. `_withdraw` transfers only the original escrowed `1000` and decrements `_orders[commitment][R]` to 0 per [5](#0-4) .
5. The remaining 50 tokens sit in the contract's balance permanently: they are not tracked by any `_orders` entry, were never emitted as `DustCollected`, and no `SweepDust` request can reference them since the dust-sweep mechanism only sweeps amounts governance explicitly knows about from tracked events, not raw contract balance minus live escrow.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L312-329)
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L630-656)
```text
    /**
     * @dev Transfers accumulated protocol dust (surplus tokens) to a specified beneficiary.
     * Called by Hyperbridge governance to sweep protocol-owned tokens that have accumulated
     * from fees, surplus splits, and calldata execution residuals.
     *
     * Supports both native tokens and ERC-20 tokens.
     *
     * @param req The sweep request containing the beneficiary address and token amounts.
     */
    function _sweepDust(SweepDust memory req) internal {
        uint256 outputsLen = req.outputs.length;
        for (uint256 i; i < outputsLen;) {
            TokenInfo memory info = req.outputs[i];
            address token = address(uint160(uint256(info.token)));
            uint256 amount = info.amount;

            if (token == address(0)) {
                _sendValue(req.beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(req.beneficiary, amount);
            }
            unchecked {
                ++i;
            }
            emit DustSwept(token, amount, req.beneficiary);
        }
    }
```
