### Title
Permissionless `CallDispatcher.dispatch()` allows draining any token/ETH dust and outstanding allowances left on the shared singleton dispatcher - ([File: evm/src/utils/CallDispatcher.sol])

### Summary
`CallDispatcher` is a single, address-deterministic (CREATE2) contract shared by every app that supports calldata execution — `IntentGatewayV2`/`IntentsBase`, `HyperFungibleToken`, and `WrappedHyperFungibleToken`. Its `dispatch(bytes)` function is `external` with **no access control and no caller restriction**, and it executes arbitrary `to.call{value}(data)` for every `Call` the caller supplies [1](#0-0) . Because the dispatcher is meant to briefly hold tokens/ETH and issue approvals while executing user- or solver-supplied `Call[]` payloads, any balance or allowance that is left on it after a legitimate flow finishes — because it wasn't part of the tracked "inputs"/"outputs" that get swept, or because a flow (like `HyperFungibleToken`/`WrappedHyperFungibleToken` calldata execution) performs no sweep at all — can be swept by **any unrelated third party** simply by calling `CallDispatcher.dispatch()` directly with their own `Call[]`, exactly matching the reported "approval farming"/arbitrary-call-drains-approval pattern.

### Finding Description
`CallDispatcher.dispatch()` decodes an attacker-supplied `Call[]` and executes each entry as `to.call{value: call.value}(call.data)`, with the only check being that `to` has code [1](#0-0) . The interface itself is documented as dispatching "untrusted call(s)" [2](#0-1) , i.e. it is deliberately open to anyone, on the assumption that it never holds value except transiently inside one atomic caller transaction.

That assumption breaks down in several concrete places:

1. **Non-tracked byproduct tokens/dust are never swept.** In `IntentGatewayV2.placeOrder`'s predispatch flow, after `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)` runs (e.g. a Uniswap swap), the contract only sweeps balances of tokens that are explicitly listed in `order.inputs` [3](#0-2) . Any other token or native remainder produced by the predispatch call (e.g. slippage residue, an intermediate swap hop token, or leftover ETH) is left permanently on the CallDispatcher.
2. Similarly, `IntentsBase._execute` only sweeps the specific `order.output.assets` tokens after running `order.output.call` [4](#0-3) ; anything else the output calldata produces or leaves behind is not recovered by the protocol.
3. **`HyperFungibleToken`/`WrappedHyperFungibleToken` calldata execution has no sweep step at all.** `onAccept` mints/unlocks tokens to `to` (which can be the `CallDispatcher`), then calls `ICallDispatcher(_dispatcher).dispatch(message.data)` and simply emits an event — there is no post-dispatch balance check or return of leftover funds [5](#0-4) . Any calldata that doesn't perfectly consume the bridged amount (rounding, partial fill, revert-tolerant multi-hop swap) leaves a residual balance stuck on the shared dispatcher indefinitely.
4. **Outstanding token approvals persist across transactions.** The project's own documentation and tests show `Call[]` payloads routinely granting `type(uint256).max` approvals from the dispatcher to routers, e.g. `IERC20.approve.selector, uniswapRouter, type(uint256).max` [6](#0-5) . The security notes for HFT explicitly acknowledge the risk: "Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution" [7](#0-6)  — but nothing in the contract enforces this, and the approval is not revoked afterwards.

Because `CallDispatcher` is one shared, permissionless, CREATE2-deployed contract used by *every* app on the chain, any dust or outstanding approval left behind by *any* order/transfer (from any user, any gateway instance, any HFT token) becomes fair game: an attacker calls `CallDispatcher.dispatch()` directly, off-path from `IntentGatewayV2`/`HyperFungibleToken`, with a `Call` such as `{to: token, value: 0, data: transfer(attacker, dispatcherBalance)}`, or — if an infinite allowance to a router/spender still exists — `{to: router, data: swapExactTokensForTokens(..., to: attacker, ...)}`, which causes the router to pull from the dispatcher's balance using its lingering approval and deliver the proceeds to the attacker.

### Impact Explanation
This allows an unprivileged attacker to steal residual tokens/ETH and abuse residual allowances on a contract that is shared by every Hyperbridge app supporting calldata execution (IntentGatewayV2, HyperFungibleToken, WrappedHyperFungibleToken, BridgeToken). The value at risk includes:
- Any dust/byproduct tokens from predispatch/postdispatch swaps that fall outside the tracked input/output token set.
- Any residual balance left after HFT/WrappedHFT calldata execution, which has no sweep logic whatsoever.
- Funds reachable through any unlimited/leftover approval a `Call[]` payload granted from the dispatcher to a router or other spender.

Since these funds ultimately originate from users' bridged/escrowed assets, this is concrete theft of user/protocol funds via a permissionless call, matching the High severity of the source report.

### Likelihood Explanation
Likelihood is elevated because:
- `dispatch()` requires zero permission or state precondition beyond `to` having code — any EOA can call it at any time.
- Multi-hop/DeFi calldata execution (swaps, especially with slippage or partial fills) commonly produces byproduct balances that the surrounding protocol code does not track/sweep.
- The project's own documentation flags unlimited approvals as a known risk pattern that SDK/integrator code is expected to avoid manually, but this is not enforced on-chain — a single order/integration using `type(uint256).max` approvals (as shown in the repo's own tests) creates a standing exposure for every future dispatcher user.
- Because the dispatcher is a shared singleton, exposure accumulates across the whole protocol's usage, not just one app instance, increasing the odds that some balance/approval exists to exploit at any given time.

### Recommendation
- Restrict `CallDispatcher.dispatch()` so it can only be invoked by a caller-scoped, per-call authorization (e.g. require the caller to be one of the registered app contracts, or require a one-time-use dispatch token/nonce set atomically by the calling app just before invoking `dispatch`), removing the "anyone can call with arbitrary calldata" surface.
- Alternatively/additionally, deploy per-flow (ephemeral) dispatcher instances via CREATE2 with a short-lived salt/nonce per order, rather than one permanent shared singleton, so leftover balances/approvals cannot be reused across unrelated future transactions.
- After every `dispatch()` invocation from `IntentGatewayV2`/`IntentsBase`/HFT, sweep the dispatcher's *entire* balance for every token touched by the calldata (not only the tracked input/output tokens), and add an equivalent sweep to the HFT/WrappedHFT `onAccept` calldata-execution path, which currently has none.
- Disallow (or require explicit exact-amount) approvals from within dispatched `Call[]` payloads, or force `approve(spender, 0)` cleanup calls appended automatically after execution, rather than relying on integrator discipline as the current docs do.

### Proof of Concept
Conceptual PoC (would need Foundry against a fork or the repo's test harness to fully execute):
1. Any user places an `IntentGatewayV2` order with a `predispatch.call` that performs `IERC20(TOKEN).approve(ROUTER, type(uint256).max)` followed by a swap producing a byproduct token `X` that is **not** part of `order.inputs` — e.g. a multi-hop swap `ETH -> X -> DAI` where only `DAI` is escrowed. `X`'s balance from an intermediate leg (or dust from imprecise routing) remains on `CallDispatcher`; `TOKEN`'s infinite allowance to `ROUTER` also remains.
2. Later, in a separate transaction, the attacker calls `CallDispatcher.dispatch(abi.encode(calls))` directly (bypassing `IntentGatewayV2` entirely) where `calls = [Call({to: X, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, X.balanceOf(dispatcher))})]`.
3. `CallDispatcher` executes the transfer as itself (`msg.sender == dispatcher` from `X`'s perspective), sending the entire stray `X` balance to the attacker — with no relationship to the original order at all.
4. Equivalently, if `TOKEN` still has an outstanding `type(uint256).max` allowance to `ROUTER` from step 1, and the dispatcher later holds any `TOKEN` balance (from any unrelated flow), the attacker can call `dispatch()` with `Call({to: ROUTER, data: swapExactTokensForTokens(amount, 0, path, attacker, deadline)})`, causing `ROUTER` to pull `TOKEN` from the dispatcher (via the existing allowance) and deliver proceeds to the attacker.

Existing repository tests (e.g. `testPostdispatchTokenSweep`, `testDustCollectionFromPredispatchSwapWithUniswapV2` in `evm/tests/foundry/IntentGatewayV2Test.sol`) confirm the pattern of the dispatcher accumulating and approving balances during normal operation [8](#0-7) ; they do not, however, test what happens when an outside party calls `CallDispatcher.dispatch()` directly against leftover state — which is the exploitable gap.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L44-61)
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
```

**File:** sdk/packages/core/contracts/interfaces/ICallDispatcher.sol (L26-37)
```text
/**
 * @title The ICallDispatcher
 * @author Polytope Labs (hello@polytope.technology)
 *
 * @notice This interface is used to dispatch untrusted call(s)
 */
interface ICallDispatcher {
    /*
     * @dev Dispatch the encoded call(s)
     */
    function dispatch(bytes memory params) external;
}
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L413-449)
```text
            // Execute the call dispatcher with predispatch call
            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);

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

            // Execute transfer calls from call dispatcher
            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L327-359)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        HyperFungibleTokenUpgradeable.Message memory message =
            abi.decode(request.body, (HyperFungibleTokenUpgradeable.Message));
        address beneficiary = _toAddr(message.to);

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

        emit Received({from: message.from, to: beneficiary, source: string(request.source), amount: message.amount});
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L1332-1392)
```text
    function testPostdispatchTokenSweep() public {
        // Test realistic postdispatch: exact output swap on Uniswap V2 where refunded input tokens are swept
        // Scenario: User wants 1000 DAI on destination, solver sends USDC to dispatcher,
        // dispatcher swaps exact output for DAI, refunded USDC is swept back to gateway

        uint256 inputAmount = 1000 * 1e6; // 1000 USDC escrow
        uint256 daiOutputAmount = 1000 * 1e18; // Exact 1000 DAI output wanted

        // Setup order inputs
        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: inputAmount});

        // Create postdispatch calls that:
        // 1. Approve Uniswap router to spend USDC
        // 2. Execute exact output swap (swapTokensForExactTokens) - USDC -> DAI
        // 3. Transfer DAI to user
        Call[] memory postdispatchCalls = new Call[](3);

        // Get quote for how much USDC needed for 1000 DAI (will be less than what solver sends)
        address[] memory path = new address[](2);
        path[0] = address(usdc);
        path[1] = address(dai);
        address uniswapRouter = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D;
        uint256[] memory amounts = IUniswapV2Router02(uniswapRouter).getAmountsIn(daiOutputAmount, path);
        uint256 usdcNeeded = amounts[0];

        // Call 1: Approve Uniswap router
        postdispatchCalls[0] = Call({
            to: address(usdc),
            value: 0,
            data: abi.encodeWithSelector(IERC20.approve.selector, uniswapRouter, type(uint256).max)
        });

        // Call 2: Exact output swap - swap USDC for exactly 1000 DAI
        postdispatchCalls[1] = Call({
            to: uniswapRouter,
            value: 0,
            data: abi.encodeWithSelector(
                bytes4(keccak256("swapTokensForExactTokens(uint256,uint256,address[],address,uint256)")),
                daiOutputAmount, // exact amount out
                type(uint256).max, // max amount in
                path,
                address(dispatcher), // tokens come back to dispatcher
                block.timestamp
            )
        });

        // Call 3: Transfer DAI to user
        postdispatchCalls[2] = Call({
            to: address(dai), value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, user, daiOutputAmount)
        });

        // Setup order output - beneficiary is dispatcher, it will receive USDC from solver
        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: usdcNeeded + 100 * 1e6}); // Solver sends more than needed

        PaymentInfo memory output = PaymentInfo({
            beneficiary: bytes32(uint256(uint160(address(dispatcher)))), // Dispatcher receives USDC
            assets: outputAssets,
            call: abi.encode(postdispatchCalls)
        });
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-97)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

```
