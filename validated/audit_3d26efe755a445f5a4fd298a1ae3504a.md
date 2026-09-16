No access control exists on `CallDispatcher.dispatch()`, and the HFT `onAccept` path does not sweep leftover token balances from the dispatcher after calldata execution (unlike `IntentsBase._execute`, which does sweep). This confirms the exploitable pattern below.

### Title
Unpermissioned `CallDispatcher.dispatch()` lets an attacker plant persistent ERC20 approvals and drain tokens later routed through the shared dispatcher - ([File: evm/src/utils/CallDispatcher.sol])

### Summary
`CallDispatcher.dispatch()` is a public, access-control-free function that executes attacker-supplied `Call[]` (arbitrary `to`/`data`) in the dispatcher's own context [1](#0-0) . The same dispatcher instance is shared across `HyperFungibleToken`/`WrappedHyperFungibleToken` (mint/unlock-then-dispatch) and `IntentGatewayV2`/`IntentsBase` (predispatch/postdispatch) flows, and is documented as a persistent, reused deployment [2](#0-1) . Because anyone can call `dispatch()` directly with arbitrary calldata, an attacker can make the dispatcher execute `token.approve(attacker, type(uint256).max)` for any ERC20, exactly analogous to the referenced bug class: an unrestricted call whose target and calldata are fully attacker-controlled and can grant token movement rights that outlive the triggering transaction.

### Finding Description
Unlike a token balance (which many flows sweep back to the caller before the transaction ends), an ERC20 `approve()` is *persistent state* that survives the transaction and any subsequent unrelated interactions with that same spender. `CallDispatcher.dispatch(bytes memory encoded)` has no caller restriction — it is not gated to `IntentGatewayV2`, `HyperFungibleToken`, or any privileged address [1](#0-0) . An attacker can call it directly with a `Call[]` of `{to: TOKEN, value: 0, data: approve(attacker, type(uint256).max)}` targeting any ERC20 with code, satisfying the only guard (`extcodesize(to) > 0`).

Once planted, this approval persists indefinitely on-chain as `allowance(dispatcher, attacker) = max`. Multiple legitimate flows subsequently move real token balances into this same dispatcher address:
- `HyperFungibleToken`/`WrappedHyperFungibleToken.onAccept()` mints/unlocks bridged tokens directly `to` the `CallDispatcher` address when calldata execution is requested, then calls `dispatch(message.data)` [3](#0-2) . There is no sweep-back of any residual/unconsumed token balance after the user's calls run (contrast with `IntentsBase._execute`, which explicitly sweeps residual balances as protocol dust) [4](#0-3) .
- `IntentGatewayV2.placeOrder` transfers `predispatch.assets` to the dispatcher before executing user-supplied predispatch calldata [5](#0-4) .

Because the dispatcher is a single, reused, unauthenticated-caller contract, any token balance that lands on it (even transiently, or as unswept dust from a slippage-tolerant swap encoded by a legitimate user's `Call[]`) is drainable by an attacker holding a previously self-granted unlimited allowance — the attacker simply calls `token.transferFrom(dispatcher, attacker, amount)` at will, exactly as in the referenced report where a pre-positioned approval is exploited by an unrelated, unrestricted call.

### Impact Explanation
This is concrete theft of funds: any ERC20 balance left on the shared `CallDispatcher` — whether from `HyperFungibleToken`/`WrappedHyperFungibleToken` calldata-bearing bridges (no sweep-back exists in that path) or from timing windows around `IntentGatewayV2` predispatch/postdispatch calls — can be siphoned by an attacker who front-loaded a malicious `approve()` via the unrestricted `dispatch()` entrypoint. Given the dispatcher is shared across many users' bridge/intent transactions on a chain, this is a High severity, protocol-wide fund-theft primitive, not limited to a single victim's own approval mistake.

### Likelihood Explanation
Likelihood is high: `dispatch()` requires no privilege and no prior interaction with the token owner — the attacker only needs the target ERC20 to have code (which it trivially does). Planting the malicious approval is a single, cheap, always-available transaction that can be executed proactively (once per token of interest) and then monitored/exploited whenever a subsequent bridge or intent transaction leaves any balance of that token on the dispatcher (e.g., swap slippage dust in the HFT calldata path, which is explicitly unswept).

### Recommendation
Restrict `CallDispatcher.dispatch()` to be callable only by explicitly authorized/whitelisted caller contracts (e.g., the specific `HyperFungibleToken`, `WrappedHyperFungibleToken`, and `IntentGatewayV2` instances), or deploy an ephemeral/ per-call dispatcher (e.g., via `CREATE2`/minimal proxy that self-destructs or is single-use) so no persistent approvals can survive across unrelated transactions. Additionally, ensure every flow that can leave a token balance on the dispatcher (including the HFT/WrappedHFT `onAccept` calldata path) sweeps 100% of the residual balance back to a safe owner within the same transaction, and consider revoking any approvals granted during `dispatch()` execution before returning control.

### Proof of Concept
1. Attacker calls `CallDispatcher.dispatch(abi.encode([Call({to: USDC, value: 0, data: abi.encodeWithSelector(IERC20.approve.selector, attacker, type(uint256).max)})]))` directly — no restriction prevents this [1](#0-0) . `allowance(dispatcher, attacker)` is now `type(uint256).max`.
2. A legitimate user bridges USDC via `HyperFungibleToken.send()` with `to = CALL_DISPATCHER` and `data` encoding a swap that doesn't consume the full minted amount (e.g., due to slippage tolerance) [6](#0-5) . On the destination chain, `onAccept()` mints USDC to the dispatcher and calls `dispatch(message.data)`; leftover USDC remains on the dispatcher with no sweep-back [3](#0-2) .
3. Attacker calls `USDC.transferFrom(dispatcher, attacker, leftoverBalance)` using the allowance from step 1, stealing the residual bridged tokens.

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

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L320-333)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L387-414)
```text
        // escrow tokens
        uint256 msgValue = msg.value;
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            // Transfer all predispatch assets to the call dispatcher
            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    (bool sent,) = dispatcher.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }

            // Execute the call dispatcher with predispatch call
            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);
```

**File:** docs/content/developers/evm/hyper-fungible-token/hyper-fungible-token.mdx (L117-162)
```text
Bridge tokens and swap to WETH via UniswapV2 on the destination chain:

```solidity lineNumbers
import {IUniswapV2Router02} from "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";

address[] memory path = new address[](2);
path[0] = DEST_TOKEN;
path[1] = WETH;

Call[] memory calls = new Call[](2);

// Approve UniswapV2 router
calls[0] = Call({
    to: DEST_TOKEN,
    value: 0,
    data: abi.encodeWithSelector(IERC20.approve.selector, UNISWAP_V2_ROUTER, amount)
});

// Swap via UniswapV2
calls[1] = Call({
    to: UNISWAP_V2_ROUTER,
    value: 0,
    data: abi.encodeWithSelector(
        IUniswapV2Router02.swapExactTokensForTokens.selector,
        amount,
        minAmountOut,
        path,
        recipientAddress,
        block.timestamp
    )
});

IHyperFungibleToken(tokenAddress).send{value: nativeFee}(
    IHyperFungibleToken.SendParams({
        dest: StateMachine.evm(42161),
        // mint to the CallDispatcher so the swap can spend the tokens
        to: abi.encodePacked(CALL_DISPATCHER),
        amount: amount,
        timeout: 3600,
        relayerFee: relayerFee,
        data: abi.encode(calls)
    })
);
```

Tokens are minted to `to` first, then the `CallDispatcher` executes each call in sequence. If the calls need to spend the minted tokens, set `to` to the `CallDispatcher` address so tokens are minted directly to the dispatcher.
```
