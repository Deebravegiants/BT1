### Title
IntentGatewayV2 credits fixed escrow amounts to orders while sweeping predispatch tokens through `CallDispatcher.dispatch`, which does not check the ERC20 boolean return value of `transfer()` - (File: evm/tron/contracts/apps/IntentGatewayV2.sol / evm/src/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.placeOrder` (predispatch path) sweeps input tokens from the `CallDispatcher` back to the gateway by building a raw `Call` whose `data` is `abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)` and executing it via `ICallDispatcher(dispatcher).dispatch(...)`. `CallDispatcher.dispatch` only checks the low-level `call` success flag, never decoding/validating the ABI-encoded boolean that ERC20 `transfer()` is supposed to return. This is exactly the ERC20-non-conformance class described in the external report: a non-reverting, non-compliant token that returns `false` on failed transfer is treated as a successful transfer.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol::placeOrder` (predispatch branch, lines ~416-449) and the structurally identical `evm/src/apps/IntentGatewayV2.sol::placeOrder`, escrowed amounts are recorded in the `_orders` mapping unconditionally: [1](#0-0) 

The actual token movement from `dispatcher` back to `address(this)` is delegated to `CallDispatcher`: [2](#0-1) 

`CallDispatcher.dispatch` only reverts if the low-level `.call` itself reverts (`success == false`); it never inspects `result` to confirm the ERC20 `transfer()` call actually returned `true`. Per the ERC20 spec (and as the referenced report states), `transfer`/`transferFrom` are only *recommended* to revert on failure — non-compliant tokens (e.g. paused/blacklist-style tokens) can simply return `false` while the outer call still succeeds. In that case `CallDispatcher.dispatch` sees `success == true` and does not revert, so `IntentGatewayV2` proceeds as if the sweep succeeded, even though the gateway never actually received the tokens.

The tron variant's `placeOrder` (lines 416-446) then unconditionally does `_orders[commitment][token] += reducedInputs[i].amount;` with no subsequent verification that the gateway's real token balance increased by that amount — unlike the mainnet `evm/src/apps/IntentGatewayV2.sol` predispatch path, which does perform a balance-diff check after the sweep and mutates `order.inputs[i].amount` to the actually-received amount: [3](#0-2) 

This means the tron deployment's escrow bookkeeping (`_orders[commitment][token]`) can be inflated relative to the contract's real on-chain token balance for that asset whenever a non-compliant ERC20 (integrated as a supported input asset) silently fails the sweep `transfer()`.

### Impact Explanation
Because `_orders[commitment][token]` is a per-order ledger drawn against the gateway's single shared token balance, an order whose escrow entry is phantom (recorded but not actually funded) can still later be refunded or paid out via `_withdraw`/`IntentsBase._withdraw`, which performs `IERC20(token).safeTransfer(beneficiary, amount)` against the *recorded* escrow amount: [4](#0-3) 

If the ledger overstates real holdings, honoring that withdrawal necessarily consumes token balance that belongs to other users' legitimately escrowed orders in the same token — i.e. theft/insolvency of other orders' escrowed funds, or a stuck/broken withdrawal path once the shared balance is exhausted (permanent freezing for the legitimate depositors). This satisfies the "concrete theft or permanent freezing of funds" bar.

### Likelihood Explanation
Exploitability depends on a non-standard-conforming ERC20 (returns `false` instead of reverting on failed transfer) being configured as a supported intent-input asset, and on that token's transfer to the gateway failing in a way that returns `false` rather than reverting (e.g., blacklist, pause, or exchange-specific fee-on-transfer edge cases hitting `require`-less code paths). Asset onboarding is presumably curated/administered, which somewhat mitigates likelihood (as the original report notes), but the codebase's own docs and `predispatch`/`postdispatch` design explicitly anticipate arbitrary DEX/tokens flowing through `CallDispatcher`, increasing the chance a non-compliant token enters this path over time.

### Recommendation
Mirror the mainnet `placeOrder`'s balance-diff verification in the tron `IntentGatewayV2.placeOrder` (and any other callers sweeping via `CallDispatcher`): after `ICallDispatcher.dispatch` returns, re-read `IERC20(token).balanceOf(address(this))` and only credit `_orders[commitment][token]` with the actually-received delta, never with the pre-computed `reducedInputs[i].amount`. Additionally, harden `CallDispatcher.dispatch` (or add a dedicated safe-sweep helper) to decode and validate the boolean return of ERC20 `transfer`/`transferFrom` calls it forwards, consistent with the `SafeERC20` usage already applied elsewhere in the codebase (`safeTransfer`/`safeTransferFrom`).

### Proof of Concept
1. Admin/governance lists a non-standard ERC20 token `T` as a valid intent input asset, where `T.transfer()` can return `false` without reverting under some condition (e.g., recipient blacklisted, contract paused, or a bugged/edge-case fee-on-transfer implementation).
2. A user calls `placeOrder` with `order.predispatch` populated so that `T` passes through the predispatch swap-then-escrow path in `evm/tron/contracts/apps/IntentGatewayV2.sol`.
3. During the sweep step, `CallDispatcher.dispatch` executes `T.transfer(address(this), balance)`; suppose this call returns `false` (e.g. the gateway itself is momentarily denylisted or the token enforces some check) but does not revert.
4. `CallDispatcher.dispatch` observes `success == true` (the outer call didn't revert) and proceeds without error.
5. `IntentGatewayV2.placeOrder` credits `_orders[commitment][T] += reducedInputs[i].amount` even though the gateway's actual `T` balance did not increase.
6. This order's escrow entry is now backed by other users' `T` deposits already present in the gateway. A subsequent refund/withdrawal path (`_withdraw`) will pay out `T` from the shared pool, depleting balance owed to other legitimate order holders — resulting in a shortfall/freeze for those users once the pool is drained.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L416-446)
```text
            // Transfer tokens from call dispatcher back to IntentGateway
            Call[] memory transferCalls = new Call[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;
                uint256 balance;

                if (token == address(0)) {
                    balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                } else {
                    balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                }

                uint256 dust = balance - requiredAmount;
                if (dust > 0) emit DustCollected(token, dust);

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }
```

**File:** evm/src/utils/CallDispatcher.sol (L44-62)
```text
    function dispatch(bytes memory encoded) external {
        Call[] memory calls = abi.decode(encoded, (Call[]));
        uint256 callsLen = calls.length;
        for (uint256 i = 0; i < callsLen; ++i) {
            Call memory call = calls[i];
            uint32 size;
            address to = call.to;
            assembly {
                size := extcodesize(to)
            }

            if (size == 0) {
                revert NotContract(to);
            }

            (bool success, bytes memory result) = to.call{value: call.value}(call.data);
            if (!success) revert CallFailed(to, result);
        }
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L291-311)
```text
            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }

                if (received > order.inputs[i].amount) {
                    uint256 dust = received - order.inputs[i].amount;
                    emit DustCollected(token, dust);
                } else {
                    order.inputs[i].amount = received;
                }

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
