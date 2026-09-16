### Title
CallDispatcher accumulates unclaimed native/ERC20 residue that any subsequent cross-chain message's attacker-controlled calldata can drain - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch()` is a shared, per-application singleton that executes fully attacker-controlled `Call{to, value, data}` arrays on behalf of *every* message/order routed through a given `HyperFungibleToken`/`WrappedHyperFungibleToken` (and `IntentGatewayV2`) deployment. It performs no accounting to ensure that a call only spends value the *current* message deposited into it, and no sweep-back of unspent residue occurs after `onAccept()` calldata execution. Combined with the documented pattern of parking native ETH in the `CallDispatcher` for `Call.value` forwarding, and swap-refund helpers that return unspent value to `msg.sender` (the `CallDispatcher` itself) rather than the true beneficiary, native ETH/WETH can accumulate in this shared contract. Any later relayed message can then supply calldata whose `Call.to`/`Call.value` targets an attacker address and siphon that accumulated balance, exactly mirroring the `LMPVaultRouter` pattern of an unvalidated, caller-controlled target draining funds that were never that caller's to take.

### Finding Description
`CallDispatcher.dispatch()` blindly forwards value to any address with code: [1](#0-0) 

It is configured once per app deployment (`WrappedConfigOptions.dispatcher` / `_dispatcher`) and reused for **every** incoming cross-chain message handled by that app instance: [2](#0-1) 

In `onAccept()`, when `_isWeth` is true, the beneficiary can be set to the `CallDispatcher` address itself so it receives unwrapped native ETH, after which the fully sender-controlled `message.data` (decoded as `Call[]`) is dispatched with no scoping to "only spend what this message just deposited": [3](#0-2) 

This "park ETH in the CallDispatcher, then let attacker-controlled calls spend it via `Call.value`" pattern is explicitly documented and encouraged: [4](#0-3) 

Crucially, the example swap helper used in that flow refunds unspent ETH to `msg.sender` — which, when invoked through `CallDispatcher.dispatch()`, is the `CallDispatcher` contract, not the message's actual beneficiary: [5](#0-4) 

Unlike `IntentGatewayV2._execute()`, which explicitly measures and sweeps back any residual balance left on the `CallDispatcher` after dispatching calldata: [6](#0-5) 

the `WrappedHyperFungibleToken`/`HyperFungibleToken` `onAccept()` path has **no equivalent sweep** after `ICallDispatcher(_dispatcher).dispatch(message.data)` — any leftover native ETH (e.g., from an over-estimated swap, a partially-consumed `Call.value`, or a message whose calldata never fully spends what was pushed) simply remains sitting in the shared `CallDispatcher`'s balance indefinitely.

Because `CallDispatcher.dispatch()` only checks `extcodesize(to) > 0` — never who deposited the funds or which message is entitled to them — any subsequent relayed cross-chain message to the same app (attacker deposits an arbitrary/minimal amount and sets `message.to = CALL_DISPATCHER`, `message.data` = an ABI-encoded `Call[]` with `{to: attackerContract, value: <observed residual balance>, data: ""}`) can drain the entire accumulated residue, which belongs to unrelated prior messages/users, not the attacker. This is structurally identical to the reported `LMPVaultRouter` bug: an unprivileged, single relayed message reaches a shared pool of funds through a caller-controlled external call target with no ownership/segregation check.

### Impact Explanation
An attacker who can dispatch (or have relayed) even one low-value cross-chain HFT/WrappedHFT message can steal all native ETH/WETH residue accumulated in the shared `CallDispatcher` from unrelated prior messages belonging to other users — a direct, unauthorized theft of funds via forged/abused calldata execution, satisfying the High-severity bar (concrete theft of funds from a reachable, unprivileged dispatch path).

### Likelihood Explanation
Likelihood is contingent on residue actually accumulating in the `CallDispatcher` (e.g., via the refund-to-`msg.sender` pattern in swap helpers, or any calldata that intentionally/accidentally under-spends the pushed value while leaving `beneficiary = CALL_DISPATCHER`). Given the documented, encouraged usage pattern of routing native value through the `CallDispatcher` for swap-and-forward calldata, and the total absence of a sweep-back safeguard on the `onAccept()` path (in contrast to `IntentGatewayV2`, which does sweep), this is a realistic and repeatable condition rather than a purely theoretical one — any user integrating the documented WETH/calldata pattern can create exploitable residue, and any subsequent relayed message can extract it.

### Recommendation
- After dispatching `message.data` in `onAccept()`/`onPostRequestTimeout()`, measure and sweep any residual native/token balance left on the `CallDispatcher` back to a safe recipient (protocol treasury) or to the originating message's beneficiary, mirroring `IntentsBase._execute()`'s sweep-back pattern.
- Alternatively, never let `CallDispatcher` hold value across transactions: require calldata to fully consume any value it receives within the same `dispatch()` call (revert on non-zero balance post-dispatch), or use a per-call ephemeral executor instead of one long-lived shared contract.
- Ensure swap/utility helpers refund unspent value to the true beneficiary address (passed explicitly), not to `msg.sender`, when invoked via `CallDispatcher`.

### Proof of Concept
1. Deploy `WrappedHyperFungibleToken` in WETH mode with a shared `CallDispatcher`.
2. User A bridges tokens with `message.to = CALL_DISPATCHER` and `data` encoding a `Call` to `UniV3UniswapV2Wrapper.swapETHForExactTokens` that over-estimates `msg.value` needed, producing a refund; per `UniV3UniswapV2Wrapper.swapETHForExactTokens` (lines 143-149), the refund is sent to `msg.sender`, i.e., the `CallDispatcher`, leaving residual ETH stranded there since `onAccept()` performs no post-dispatch sweep.
3. Attacker (User B) relays a minimal cross-chain message to the same `WrappedHyperFungibleToken`, setting `message.to = CALL_DISPATCHER` and `message.data` to an ABI-encoded `Call[]` = `[{to: attackerContract, value: <CallDispatcher.balance>, data: ""}]`.
4. `onAccept()` calls `ICallDispatcher(_dispatcher).dispatch(message.data)`, which forwards the entire stranded ETH balance (belonging to User A's transaction) to the attacker's contract, since `dispatch()` performs no ownership check — only `extcodesize(to) > 0`.

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L55-86)
```text
    struct WrappedConfigOptions {
        /// @notice Address of the ISMP host contract on this chain
        address host;
        /// @notice Address of the CallDispatcher contract for executing calldata on receive
        address dispatcher;
        /// @notice Address of the underlying ERC20 token to wrap
        address underlying;
        /// @notice Whether the underlying token is WETH (enables native ETH refunds on timeout)
        bool isWeth;
    }

    /// @notice Thrown when the provided bytes are too short to extract an address
    error InvalidAddress(uint256 length);


    /// @notice Thrown when a native ETH transfer fails during timeout refund
    error TransferFailed();

    /// @notice Thrown when attempting to send to or receive from an unconfigured chain
    error UnsupportedChain();

    /**
     * @notice Thrown when the source address of an incoming message does not match the
     * expected contract address for that chain
     */
    error UnauthorizedSource();

    /// @notice Address of the ISMP host contract on this chain
    address internal _host;

    /// @notice Address of the CallDispatcher contract for executing destination calldata
    address internal _dispatcher;
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L309-328)
```text
        if (_isWeth) {
            // Try a native-ETH push first (cheap for EOAs and payable contracts);
            // if the recipient cannot accept native value (no `receive()` / `fallback()
            // payable`), re-wrap the withdrawn ETH and deliver the underlying WETH as
            // an ERC-20 transfer instead. This mirrors the deposit-side flexibility of
            // `send()` (which accepts WETH from non-payable callers via `safeTransferFrom`)
            // so the refund path doesn't permanently lock funds for the same caller class.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = beneficiary.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }
```

**File:** docs/content/developers/evm/hyper-fungible-token/wrapped-hyper-fungible-token.mdx (L164-203)
```text
When `isWeth = true`, the WrappedHFT unwraps WETH to native ETH on receive. This example bridges WETH back to the home chain, where it's unwrapped to native ETH and swapped for an exact amount of USDC via UniswapV2. The `Call.value` field forwards the native ETH to the router — demonstrating that the `CallDispatcher` can hold and forward native tokens:

```solidity lineNumbers
import {IUniswapV2Router02} from "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";

address[] memory path = new address[](2);
path[0] = WETH;
path[1] = USDC;

Call[] memory calls = new Call[](1);

// Swap native ETH → exact USDC via UniswapV2
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

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L140-149)
```text
        bytes[] memory results = IMulticallExtended(_params.swapRouter).multicall(deadline, data);
        uint256 spent = abi.decode(results[0], (uint256));

        if (spent < msg.value) {
            uint256 refund = msg.value - spent;
            IWETH(weth).withdraw(refund);

            (bool success,) = msg.sender.call{value: refund}("");
            if (!success) revert RefundFailed();
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
