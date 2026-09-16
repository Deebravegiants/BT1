### Title
Unchecked ERC20 `transfer` return value in `CallDispatcher`-routed sweeps lets residual tokens be stolen from the permissionless `CallDispatcher` - (File: evm/src/utils/CallDispatcher.sol)

### Summary
`CallDispatcher.dispatch()` only checks that the low-level `.call` did not revert; it never inspects the boolean return value of the encoded call. `IntentGatewayV2` and `IntentsBase` build ERC20 "sweep" calls using the raw `IERC20.transfer.selector` (not `SafeERC20`) and route them through this same `CallDispatcher`. For a non-standard ERC20 that returns `false` on failure instead of reverting, the sweep silently "succeeds" while the tokens remain stuck on the `CallDispatcher`. Because `CallDispatcher.dispatch()` has no access control and is a single shared, reusable contract, any external actor can subsequently call it directly to drain those stranded tokens.

### Finding Description
`CallDispatcher.dispatch` executes each `Call` with a raw low-level call and only reverts if the call itself reverts: [1](#0-0) 

`IntentGatewayV2.placeOrder` builds sweep calls for pulling escrowed input tokens back from the (untrusted, dust-holding) `dispatcher` using the raw ERC20 selector rather than `safeTransfer`: [2](#0-1) 

The same unchecked-selector pattern is used for post-fill dust sweeping in `IntentsBase._execute`, where any residual balance on the dispatcher is "transferred" back and unconditionally counted/emitted as swept dust: [3](#0-2) [4](#0-3) 

The `dispatch()` function itself has no caller restriction — it's a generic public utility meant to be invoked mid-transaction by the intents/token-bridge contracts, but nothing stops any external account from calling it directly at any time: [5](#0-4) 

If an input/output token used in an order is a non-standard ERC20 that returns `false` (rather than reverting) when a `transfer` fails — e.g., due to an allowance/blacklist/pause condition triggered mid-flow, or any token whose `transfer` can return `false` — the sweep call inside `dispatch()` reports `success = true` even though no tokens moved. The tokens remain on the `CallDispatcher` contract's balance after the enclosing transaction (`placeOrder` / fill) completes normally. Because `CallDispatcher` is a single, shared, permissionless contract (its address is reused across all gateway/token-bridge calls), any third party can subsequently call `CallDispatcher.dispatch()` themselves with a `Call{to: token, data: transfer(attacker, balance)}` to steal the stranded tokens.

### Impact Explanation
This is a direct token-theft vector: legitimate user/solver funds that get "stuck" in the shared `CallDispatcher` due to an unchecked non-reverting ERC20 transfer failure are freely claimable by any unrelated third party, since `dispatch()` performs no access control and no return-data validation. This satisfies the "concrete theft of funds" bar for High severity — it is not merely internal dust misaccounting; it is externally, permissionlessly exploitable against any funds resting on that address.

### Likelihood Explanation
Exploitability depends on encountering a non-standard ERC20 configured as an order input/output that can return `false` instead of reverting on a failed `transfer` (fee-on-transfer tokens with insufficient balance checks, tokens with transfer hooks that can silently no-op, blacklist/pausable tokens, etc.) — a well-known and common class of "unusual" ERC20 behavior explicitly called out in the reference report. Given `IntentGatewayV2`/`IntentsBase` do not restrict which ERC20s can be used as order inputs/outputs, and `CallDispatcher.dispatch()` is entirely permissionless, any attacker who notices (or engineers, via a token they control being whitelisted as an order asset) a stuck balance can trivially claim it in a separate transaction.

### Recommendation
- Use `SafeERC20.safeTransfer`/`safeTransferFrom` (already used elsewhere in the codebase, e.g. `safeTransferFrom` calls) for every ERC20 call encoded and routed through `CallDispatcher`, instead of raw `IERC20.transfer.selector`.
- Additionally harden `CallDispatcher.dispatch` itself to decode and validate any `bool` return data for calls matching ERC20 transfer/approve selectors, or restrict `dispatch()` callers (e.g., only allow the configured gateway/token contracts) so stray balances cannot be swept by arbitrary third parties.
- Consider adding balance-diff assertions after each sweep call so a partially-failed or no-op transfer causes the whole transaction to revert rather than silently under-crediting escrow/dust.

### Proof of Concept
1. Configure (or have governance whitelist) a non-standard ERC20 token `T` as an order's output asset, where `T.transfer` returns `false` on some failure condition instead of reverting (e.g., a token with a blacklist check that returns `false`).
2. A solver fills an order with output calldata (`order.output.call` non-empty) using token `T`; after the calldata executes, `IntentsBase._execute` computes `balance = IERC20(T).balanceOf(dispatcher)` and builds a sweep `Call` using `IERC20.transfer.selector` back to the gateway, per `evm/src/apps/intentsv2/IntentsBase.sol:517-528`.
3. If `T.transfer` returns `false` for this particular sweep (e.g., temporary blacklist state on the dispatcher address), `CallDispatcher.dispatch` still reports `success = true` (per `evm/src/utils/CallDispatcher.sol:59-60`) since the call itself did not revert. The transaction completes, and event `DustCollected(token, balance)` is emitted despite the tokens still sitting on the `CallDispatcher` contract.
4. Any attacker now calls `CallDispatcher.dispatch(abi.encode([Call({to: T, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, balance)})]))` directly — this succeeds because `dispatch()` has no caller restriction — draining the stranded tokens.

### Citations

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

**File:** evm/src/apps/IntentGatewayV2.sol (L273-289)
```text
                } else {
                    uint256 balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    balancesBefore[i] = IERC20(token).balanceOf(address(this));
                }

                unchecked {
                    ++i;
                }
            }

            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L517-528)
```text
            } else {
                uint256 balance = IERC20(token).balanceOf(dispatcher);
                if (balance > 0) {
                    sweepCalls[sweepCount] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    sweepCount++;
                    emit DustCollected(token, balance);
                }
            }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L535-544)
```text
        if (sweepCount > 0) {
            Call[] memory finalCalls = new Call[](sweepCount);
            for (uint256 i; i < sweepCount;) {
                finalCalls[i] = sweepCalls[i];
                unchecked {
                    ++i;
                }
            }
            ICallDispatcher(dispatcher).dispatch(abi.encode(finalCalls));
        }
```

**File:** sdk/packages/core/contracts/interfaces/ICallDispatcher.sol (L32-37)
```text
interface ICallDispatcher {
    /*
     * @dev Dispatch the encoded call(s)
     */
    function dispatch(bytes memory params) external;
}
```
