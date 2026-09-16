### Title
Escrow release/refund to a USDC-blacklisted beneficiary permanently DoSes fund settlement in IntentGatewayV2's `withdraw()` - (File: `evm/src/apps/intentsv2/IntentsBase.sol`, `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`IntentGatewayV2`/`IntentsBase` releases escrowed order tokens directly to the `beneficiary` address inside `withdraw()`/`_withdraw()`, which is invoked from `onAccept()` (cross-chain `RedeemEscrow`/`RefundEscrow` messages delivered by the ISMP host) and from `onGetResponse()` (cross-chain cancel-from-source flow). If the beneficiary token is USDC (or any blacklist-capable stablecoin) and the beneficiary address has been blacklisted, the internal transfer call reverts, causing the entire message-handling call to revert — exactly the JOJO liquidation bug class, but here it blocks intent settlement/refund instead of loan liquidation.

### Finding Description
`withdraw()` (Tron variant, structurally identical to the EVM `IntentsBase._withdraw`) iterates over escrowed tokens and pushes them straight to `beneficiary` via a low-level ERC20 `transfer` call that reverts on failure: [1](#0-0) 

This function is reached from two permissionless, unprivileged-message-dispatch paths:

1. **`onAccept()`** for `RequestKind.RedeemEscrow` / `RequestKind.RefundEscrow` — triggered when the ISMP host delivers a relayed cross-chain settlement/refund message (e.g. after a solver fills an order on the destination chain, or after a destination-side cancel): [2](#0-1) 

2. **`onGetResponse()`** for the source-chain cancellation flow, invoked when Hyperbridge delivers the storage-proof response confirming the order was never filled: [3](#0-2) 

Both paths are permissionless — any relayer can submit the finalized proof, and the beneficiary is either the original order user (refund/cancel case) or the solver (fill case), addresses that are entirely attacker/third-party controlled and not validated against any blacklist prior to escrow. If the token is USDC and the beneficiary becomes blacklisted between order placement and settlement, the `transfer` call reverts, the whole `onAccept`/`onGetResponse` invocation reverts, and — unlike `EvmHost.dispatchTimeOut`, which explicitly catches failure and re-queues the commitment for retry (`if (!success) { _requestCommitments[commitment] = meta; return; }`, see `evm/src/core/EvmHost.sol:885-906`) — there is no such fallback for `onAccept`/`onGetResponse` delivery of successful (non-timeout) messages. The escrow tokens for that specific commitment become permanently stuck in the gateway contract, since `withdraw()` is the only code path that releases `_orders[commitment][token]`, and it always attempts a direct push-transfer to the potentially-blacklisted beneficiary with no way to redirect or later reclaim.

The mainline EVM/Solidity intent gateway (`IntentsBase._withdraw`, `evm/src/apps/intentsv2/IntentsBase.sol`) documents the identical push-transfer design.

### Impact Explanation
This is a direct analog to the JOJO M-4 finding: a single unprivileged actor (order placer or solver) with a USDC blacklist status can cause escrowed input tokens (which can be USDC on the source chain) to become permanently unredeemable — funds are locked in the `IntentGatewayV2` contract indefinitely with no alternate withdrawal mechanism, since the transfer is embedded in the only settlement/refund code path. This constitutes concrete, permanent freezing of user/solver funds and blocks a legitimate settlement route from ever delivering, matching the required impact bar (permanent freezing of funds / route unable to deliver messages).

### Likelihood Explanation
Requires only that: (1) a user places an order with USDC as an input token (a normal, expected use case since USDC is explicitly used throughout the test-suite as the input token, e.g. `evm/tests/foundry/IntentGatewayV2Test.sol`), and (2) that user (or the filling solver, for the `RedeemEscrow` beneficiary path) gets blacklisted by Circle at any point before settlement finalizes. This is entirely plausible given real-world sanctions/compliance blacklisting events, and requires no cooperation from Hyperbridge governance, relayers, or protocol operators — it is triggered purely by external USDC blacklist action against a normal, unprivileged protocol user.

### Recommendation
Do not push tokens directly to the beneficiary inside `withdraw()`/`onAccept()`/`onGetResponse()`. Instead:
1. Credit the beneficiary's balance in an internal claims/escrow mapping when settlement/refund is finalized, and expose a separate `claim()`/`withdraw()` function that the beneficiary (or an authorized alternate address) calls to pull funds later.
2. Alternatively, wrap the token transfer in a try/catch (or a low-level call check) so that failure to transfer does not revert the whole message-handling flow; on failure, fall back to crediting an internal claimable balance for the beneficiary instead of reverting the entire settlement.

### Proof of Concept
1. User places a same-chain or cross-chain order in `IntentGatewayV2`, escrowing USDC as `order.inputs[0]`.
2. Before the order is filled/cancelled and the ISMP settlement/refund message is finalized, USDC blacklists the order user's address (or the solver's address, in the `RedeemEscrow` beneficiary-is-solver case).
3. A relayer submits the finalized `RedeemEscrow`/`RefundEscrow` post request (or GET response for cancel) to `onAccept()`/`onGetResponse()`.
4. Inside `withdraw()`, the ERC20 `transfer` call to the blacklisted `beneficiary` reverts (`TransferFailed()`), reverting the entire `onAccept`/`onGetResponse` call. [4](#0-3) 
5. Because there is no retry-with-fallback mechanism (unlike `EvmHost.dispatchTimeOut`'s explicit re-queue-on-failure pattern), the escrowed USDC for that commitment remains permanently locked in the gateway with no available recovery path as long as the beneficiary stays blacklisted — and no other function can release `_orders[commitment][token]`.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-722)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
```
