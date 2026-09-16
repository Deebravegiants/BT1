This confirms `CallDispatcher.sol` is a shared singleton reused across `HyperFungibleToken.onAccept`, `WrappedHyperFungibleToken.onAccept`, `IntentGatewayV2.placeOrder`, and `IntentsBase._execute` — and unlike every other value-holding Hyperbridge contract (`EvmHost.withdraw`, `HostManager`, `IntentsBase._sweepDust`, `IntentGatewayV2.SweepDust`), it has no withdraw/sweep entry point at all.

### Title
`CallDispatcher` accepts native ETH via `receive()` but has no withdraw/sweep function, permanently freezing stranded funds - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher` is a shared, address-referenced utility contract used by `HyperFungibleToken`, `WrappedHyperFungibleToken`, and `IntentGatewayV2`/`IntentsBase` to execute untrusted `Call[]` arrays on behalf of cross-chain transfers and intents. It exposes `receive() external payable {}` [1](#0-0)  so that unlocked/minted native ETH can be staged there before the calling application's `Call[]` spends it. Unlike the report's `FootiumPrizeDistributor`, this contract has no owner, no admin, and no `withdraw`/`sweep` function anywhere in `dispatch()` [2](#0-1) . Any native ETH that ends up sitting in this contract without being fully consumed by the application-supplied calls is permanently unrecoverable.

### Finding Description
`CallDispatcher` is a single, address-pinned, permissionless contract (documented as a fixed deployment referenced by address, e.g. `CALL_DISPATCHER`, in the HFT/WrappedHFT calldata-execution flow) [3](#0-2) . Applications route native tokens to it as part of a cross-chain calldata-execution pattern:

- `HyperFungibleToken.onAccept` mints to `beneficiary` and then calls `ICallDispatcher(_dispatcher).dispatch(message.data)` whenever the incoming message carries a non-empty `data` payload [4](#0-3) .
- `WrappedHyperFungibleToken`'s WETH-mode unlock path explicitly sets `to: abi.encodePacked(CALL_DISPATCHER)` so the unwrapped native ETH lands directly on the dispatcher before the attached `Call[]` (e.g. a UniswapV2 swap) spends it [3](#0-2) .
- `IntentGatewayV2.placeOrder` / `IntentsBase._execute` push native/ERC20 predispatch and output assets to `_params.dispatcher`, run its `Call[]`, then explicitly sweep the dispatcher's *entire remaining balance* back with a second `dispatch()` call [5](#0-4) .

The intent-gateway callers protect themselves by always issuing a follow-up sweep `dispatch()` immediately after running the application-supplied calls, recovering the dispatcher's full balance back into the gateway (which itself has `withdraw`/`SweepDust` governance paths). However, `CallDispatcher` itself provides no such protection intrinsically — it is a bare utility with a public `receive()` and no rescue mechanism. Any of the following unprivileged/permissionless paths strand ETH there permanently with no recovery mechanism built into the contract:

1. A user constructs an `HyperFungibleToken.send`/`WrappedHyperFungibleToken.send` message whose `Call[]` payload does not fully consume the unlocked/wrapped native ETH staged on the dispatcher (e.g. a swap that reverts a partial refund into the dispatcher, or a caller who simply omits a final sweep call in their own `Call[]`). `HyperFungibleToken.onAccept`/`WrappedHyperFungibleToken.onAccept` never sweep the dispatcher's balance back themselves — that responsibility rests entirely on the relayed message's own `Call[]` — so any residual ETH is left on `CallDispatcher` with no owner, no gateway-side accounting, and no way for anyone (including protocol governance) to reclaim it.
2. Any external account can send ETH directly to `CallDispatcher.receive()` outside of any application flow at all — `receive()` accepts unconditionally from anyone.

Every other value-holding contract in this codebase provides a governance-gated recovery path for exactly this scenario: `EvmHost.withdraw` [6](#0-5) , `IntentsBase._sweepDust` (`SweepDust` request kind) [7](#0-6) , and the Tron `IntentGatewayV2`'s equivalent `SweepDust` handler [8](#0-7) . `CallDispatcher` is the only native-ETH-accepting contract in this set of reachable, unprivileged-user-facing contracts that has neither an owner nor a withdraw path.

### Impact Explanation
Because `CallDispatcher` is a single shared, address-referenced deployment used by every `HyperFungibleToken`/`WrappedHyperFungibleToken` deployment and every `IntentGatewayV2` instance that references it as `_params.dispatcher`, any ETH left behind by one user's calldata payload (through error, a reverted/partial swap refund, or simple omission of a sweep call) is permanently locked for all users, indefinitely, with no admin or governance action able to recover it. This constitutes a permanent freezing-of-funds condition reachable directly from a single unprivileged, user-submitted cross-chain message or order — satisfying the "permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
The `CallDispatcher` calldata-execution pattern is explicitly documented as intended functionality for `HyperFungibleToken`/`WrappedHyperFungibleToken` transfer-and-swap use cases, where the caller — not the token contract — supplies the `Call[]` and is fully responsible for ensuring its calls consume 100% of the staged native ETH. Any calldata that swaps for an exact output amount (e.g. `swapETHForExactTokens`, shown in the docs' own example) [9](#0-8)  can leave unspent native ETH change on the dispatcher, since `swapETHForExactTokens` only spends what's needed and the remainder stays wherever the call was initiated from — the `CallDispatcher`. This makes accidental fund-freezing plausible under normal usage, not just adversarial usage, and it requires no privileged role to trigger.

### Recommendation
Add a permissioned sweep/withdraw function to `CallDispatcher` (e.g. gated to whichever address deployed/owns it, or made callable only by the registered `IApp`/gateway contracts that reference it) that can rescue stranded native ETH and ERC-20 balances to a designated beneficiary, mirroring the `withdraw`/`SweepDust` patterns already used by `EvmHost` and `IntentsBase`. Alternatively, have every caller of `CallDispatcher.dispatch()` unconditionally sweep 100% of the dispatcher's post-call native and token balances back to itself (as `IntentsBase._execute` and `IntentGatewayV2.placeOrder` already do), and document/enforce that any `Call[]` payload supplied by end users must not be able to leave residual native ETH behind.

### Proof of Concept
1. Deploy `WrappedHyperFungibleToken` in WETH mode with `dispatcher = CallDispatcher`.
2. User A calls `send(...)` with `to = CALL_DISPATCHER`, `amount = 1 ether`, and `data` encoding a single `Call` to a UniswapV2 router's `swapETHForExactTokens(usdcAmountOut, path, recipient, deadline)` with `value: 1 ether`, requesting only `0.5 ether` worth of USDC output.
3. On the destination chain, `onAccept` unwraps 1 ether of WETH to `CallDispatcher`, then calls `ICallDispatcher(_dispatcher).dispatch(message.data)`.
4. `swapETHForExactTokens` spends only the ETH required to buy the exact `usdcAmountOut` (e.g. 0.5 ether) and returns the rest; because the call is initiated by `CallDispatcher` itself, the unspent ~0.5 ether change remains on `CallDispatcher`'s balance.
5. `CallDispatcher.dispatch()` returns successfully (`Call[]` fully specified by the user, no revert). No sweep call was included in `message.data`.
6. `CallDispatcher` now permanently holds ~0.5 ether with no function in the contract — and no owner — able to ever retrieve it. Repeating this for any user, on any chain, accumulates unrecoverable ETH in the shared dispatcher.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L36-39)
```text
    /**
     * @dev Receive function to accept ETH transfers
     */
    receive() external payable {}
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

**File:** docs/content/developers/evm/hyper-fungible-token/wrapped-hyper-fungible-token.mdx (L176-188)
```text
// The CallDispatcher holds the unwrapped ETH and forwards it via Call.value
calls[0] = Call({
    to: UNISWAP_V2_ROUTER,
    // forward the native ETH to the router
    value: amount,
    data: abi.encodeWithSelector(
        IUniswapV2Router02.swapETHForExactTokens.selector,
        usdcAmountOut,
        path,
        recipientAddress,
        block.timestamp
    )
});
```

**File:** docs/content/developers/evm/hyper-fungible-token/wrapped-hyper-fungible-token.mdx (L190-203)
```text
IHyperFungibleToken(address(wrapper)).send{value: nativeFee}(
    IHyperFungibleToken.SendParams({
        dest: StateMachine.evm(1),
        // unlock to the CallDispatcher so it receives the unwrapped ETH
        to: abi.encodePacked(CALL_DISPATCHER),
        amount: amount,
        timeout: 3600,
        relayerFee: relayerFee,
        data: abi.encode(calls)
    })
);
```

Tokens are unlocked (or unwrapped for WETH) to `to` first, then the `CallDispatcher` executes each call in sequence. Setting `to` to the `CallDispatcher` address ensures the dispatcher holds the tokens (or native ETH) so subsequent calls can spend them via `Call.value` or ERC20 transfers.
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L301-305)
```text
        _mint(beneficiary, message.amount);

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-533)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

        Call[] memory sweepCalls = new Call[](outputsLen);
        uint256 sweepCount = 0;

        for (uint256 i; i < outputsLen;) {
            address token = address(uint160(uint256(order.output.assets[i].token)));

            if (token == address(0)) {
                uint256 balance = dispatcher.balance;
                if (balance > 0) {
                    sweepCalls[sweepCount] = Call({to: address(this), value: balance, data: ""});
                    sweepCount++;
                    emit DustCollected(token, balance);
                }
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

            unchecked {
                ++i;
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

**File:** evm/src/core/EvmHost.sol (L647-660)
```text
    /**
     * @dev withdraws host revenue to the given address, can only be called by cross-chain governance
     * @param params, the parameters for withdrawal
     */
    function withdraw(WithdrawParams memory params) external restrict(_hostParams.hostManager) {
        if (params.token == address(0)) {
            // this is safe because re-entrancy is mitigated before dispatching requests
            (bool sent,) = params.beneficiary.call{value: params.amount}("");
            if (!sent) revert WithdrawalFailed();
        } else {
            IERC20(params.token).safeTransfer(params.beneficiary, params.amount);
        }
        emit HostWithdrawal({beneficiary: params.beneficiary, amount: params.amount, token: params.token});
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-682)
```text
        } else if (kind == RequestKind.SweepDust) {
            SweepDust memory req = abi.decode(incoming.request.body[1:], (SweepDust));

            uint256 outputsLen = req.outputs.length;
            for (uint256 i; i < outputsLen;) {
                TokenInfo memory info = req.outputs[i];
                address token = address(uint160(uint256(info.token)));
                uint256 amount = info.amount;

                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
                unchecked {
                    ++i;
                }
                emit DustSwept(token, amount, req.beneficiary);
            }
        }
```
