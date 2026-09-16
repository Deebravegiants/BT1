### Title
Escrow withdrawal in `IntentsBase._withdraw` bundles a mandatory fee-token transfer with the principal-token refund/release, so a single frozen/paused fee token permanently bricks unrelated escrowed funds - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentsBase._withdraw`, the single internal function used to both release escrow to a solver (`RedeemEscrow`) and refund escrow to a user (`RefundEscrow`), atomically bundles the transfer of the order's principal tokens with an unconditional transfer of accumulated Hyperbridge relayer fees denominated in the protocol's `feeToken`. If that `feeToken.safeTransfer` call reverts for any reason unrelated to the principal tokens being withdrawn (blacklisted beneficiary on a censorable stablecoin, or the fee token itself being paused), the entire withdrawal reverts — including the unrelated principal-token refund — with no way to retry the two pieces independently.

### Finding Description
`_withdraw` is called from `onAccept` for both `RedeemEscrow` and `RefundEscrow` message kinds, and internally in the same-chain fill/cancel paths: [1](#0-0) 

The function performs two unrelated actions inside one non-separable code path when `finalize == true`:
1. Transfers each of `body.tokens` (the order's actual escrowed principal, e.g. USDC/DAI/ETH the user or solver is owed) to `beneficiary`.
2. Unconditionally also transfers any accumulated `TRANSACTION_FEES` balance in `IDispatcher(host()).feeToken()` to the same `beneficiary`, via `IERC20(...).safeTransfer(...)`.

`safeTransfer` reverts the whole call if the ERC-20 transfer returns false or reverts (e.g. Circle-style blacklist on `beneficiary`, or the fee token contract being paused). Because both actions execute in the same, non-reentrant, all-or-nothing internal call, a revert in step 2 unwinds step 1 as well — even though the principal tokens have nothing to do with the fee token and are otherwise fully redeemable.

This is invoked from the cross-chain message handler: [2](#0-1) 

and identically in the Tron variant: [3](#0-2) 

Because `onAccept` is the terminal handler for an already-verified, committed cross-chain `RefundEscrow`/`RedeemEscrow` request (dispatched with `timeout: 0`, i.e. no expiry, in `_cancelFromDest`/similar paths), a relayer cannot choose an alternate calldata to work around the revert: redelivering the same commitment will hit the exact same fee-token transfer and revert again, indefinitely, until the fee-token-level restriction (blacklist or pause) is lifted by a third party outside the protocol's control.

This mirrors the Tokemak bug class exactly: a withdrawal path that is otherwise fully satisfiable is made conditional on a mandatory, unrelated action (there: staking TOKE into `gpToke`; here: transferring accrued relayer fees in the protocol fee token) whose own independent validity constraints (there: min/max stake amount, pause; here: blacklist/pause of the fee token) can revert and permanently brick the withdrawal of otherwise-recoverable escrowed funds.

### Impact Explanation
A single condition on the `feeToken` (which is a governance-configured, censorable stablecoin in the intended deployment, per `IDispatcher(host()).feeToken()`) can permanently freeze the principal escrow of any order whose finalize-time withdrawal happens to also carry a non-zero `TRANSACTION_FEES` balance for that beneficiary — this is not a niche edge case, since `TRANSACTION_FEES` are recorded whenever the user pays a relayer fee at `placeOrder`, which is the common case. The blast radius is broader than the original Tokemak finding: whereas GPToke pausing only affects the reward accrual for TOKE stakers, a fee-token freeze/pause here blocks recovery of the user's/solver's entire principal (potentially large amounts across many orders), not just a small reward. This satisfies "permanent freezing of funds."

### Likelihood Explanation
The trigger conditions are realistic and outside the gateway's control: the fee token is expected to be a mainstream stablecoin (USDC/USDT-class), which routinely implements issuer-side blacklisting and can be paused; a beneficiary being blacklisted (e.g., sanctioned address, compromised wallet flagged by the issuer) or the token being globally paused are both externally-triggerable events with no governance action on Hyperbridge's side able to unstick the specific commitment, since `_withdraw`'s all-or-nothing structure gives no path to skip or defer the fee transfer.

### Recommendation
Decouple the fee-token payout from the principal-token withdrawal: attempt fee transfer with a try/catch (or a low-level call that only reverts the fee leg) so a failure there does not roll back the principal transfers, and instead accrues the failed fee amount for later separate claim/sweep; alternatively, move the `TRANSACTION_FEES` payout to a separate, independently callable function so a stuck fee transfer cannot hold hostage an otherwise fully redeemable principal escrow.

### Proof of Concept
1. Governance configures the intent gateway's Hyperbridge host `feeToken` to a censorable stablecoin (e.g. USDC).
2. A user places a cross-chain order via `placeOrder`, paying a non-zero relayer fee, which is escrowed under `_orders[commitment][TRANSACTION_FEES]` (see `evm/src/apps/intentsv2/ExtrinsicIntents.sol` fee accounting, mirrored by `_post`).
3. The order is later cancelled from the destination chain (`_cancelFromDest`), dispatching a `RefundEscrow` message back to source with `beneficiary = order.user`.
4. Before the message is delivered, the fee-token issuer blacklists `order.user`'s address (or pauses the token globally).
5. The relayer delivers the `RefundEscrow` request; `onAccept` → `_withdraw(body, true, true)` runs: the principal-token loop succeeds, but `IERC20(feeToken).safeTransfer(beneficiary, fees)` reverts.
6. The whole `onAccept` call reverts. The commitment has `timeout: 0`, so it never times out; every re-delivery attempt hits the same revert, permanently freezing the user's escrowed principal until the blacklist/pause is lifted by the token issuer, an event outside the protocol's control. [4](#0-3)

### Citations

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-337)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-723)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

        // redeem escrowed tokens
        uint256 len = body.tokens.length;
        for (uint256 i; i < len;) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
            unchecked {
                ++i;
            }
        }

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }
```
