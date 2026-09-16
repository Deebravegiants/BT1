## Title
`CallDispatcher.dispatch` has no caller restriction, allowing any unprivileged actor to sweep tokens left in transit by IntentGatewayV2 or HyperFungibleToken - (File: evm/src/utils/CallDispatcher.sol)

### Summary
The Symmetry report describes a program that forwards unvalidated instruction data/accounts to an external CPI (`prism aggregator`) and only validates the change in balance of two specific token accounts, allowing an attacker to reroute funds through arbitrary accounts because nothing constrains *who* may invoke the CPI or *which* balances it may touch. Hyperbridge's `CallDispatcher` contract has the analogous flaw in EVM form: `dispatch(bytes memory encoded)` executes an arbitrary caller-supplied `Call[]` against any target with no access control at all, and the applications that route funds through it (`IntentGatewayV2`, `HyperFungibleToken`) only verify balance deltas for the specific tokens *they* care about, not that the dispatcher's balance is otherwise empty/uncompromised.

### Finding Description
`CallDispatcher.dispatch` is a public, unrestricted forwarder: [1](#0-0) 

It has no `onlyGateway`/`onlyHost`/ownership check — literally any address can call it directly (bypassing `IntentGatewayV2` or `HyperFungibleToken` entirely) with any `Call[]` targeting any contract holding a balance inside `CallDispatcher`.

`IntentGatewayV2.placeOrder` routes user assets through this shared dispatcher for predispatch swaps: it transfers `order.predispatch.assets` to the dispatcher, executes attacker/user-supplied calldata via `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)`, and then only sweeps back the *specific* `order.inputs[i]` token balances that it expects: [2](#0-1) 

Any token balance left in the dispatcher that is *not* one of `order.inputs[i]` (e.g., an intermediate swap-hop token, unwrapped WETH, airdropped/reward tokens, or dust from a slippage mismatch) is never swept by the gateway logic and remains sitting in the shared `CallDispatcher` contract. Because `dispatch()` has no access control, that residual balance can be drained by any unrelated address in a completely separate transaction, with a single `Call{to: token, data: transfer(attacker, balance)}`.

The same pattern is documented for `HyperFungibleToken`'s calldata-execution feature, which also forwards to the same class of `CallDispatcher`, noting "the dispatcher contract holds tokens temporarily during execution": [3](#0-2) 

Just as in the Symmetry bug — where `buy_state_rebalance` only checked `pda_usdc_account`/`pda_token_account` deltas and let an attacker pass arbitrary `TokenAccounts` through `remaining_accounts` to the untrusted CPI — `IntentGatewayV2` and `HyperFungibleToken` only check the specific tokens they expect on `CallDispatcher`, while `CallDispatcher.dispatch` itself performs zero validation of caller identity or of which balances/accounts are touched.

### Impact Explanation
Any token or ETH balance transiently or residually held by `CallDispatcher` — arising from normal predispatch/postdispatch swap slippage, intermediate-hop tokens, or a stuck mint-then-execute flow in `HyperFungibleToken.onAccept` — is not custodied by any access-controlled contract and can be permanently stolen by any unprivileged third party who simply calls `CallDispatcher.dispatch()` directly. This is a concrete theft-of-funds vector reachable by anyone monitoring on-chain state for a nonzero token balance on the shared dispatcher address, with no order, solver, or relayer privilege required.

### Likelihood Explanation
`CallDispatcher` is a single shared, publicly deployed contract used by both `IntentGatewayV2` predispatch/postdispatch flows and `HyperFungibleToken`/`WrappedHyperFungibleToken` calldata execution. Any imperfect sweep (slippage residue, an intermediate-hop token not in `order.inputs`/`order.output.assets`, a reverted downstream leg that still leaves partial balances, or a delayed relay of `HyperFungibleToken` calldata) leaves exploitable value sitting at a well-known, unprotected address, making exploitation straightforward and requiring only a public RPC call.

### Recommendation
Restrict `CallDispatcher.dispatch` to only be callable by authorized/trusted callers (e.g., an allow-list of registered gateway/app contracts, or make `CallDispatcher` a per-call, ephemeral/minimal-proxy instance rather than a shared long-lived contract). Additionally, `IntentGatewayV2` should sweep *all* residual balances left on the dispatcher after each dispatch (not only the tokens explicitly listed in `order.inputs`/`order.output.assets`), and `HyperFungibleToken`'s `onAccept` calldata execution should assert the dispatcher's balance for the bridged token returns to zero after `ICallDispatcher.dispatch` returns.

### Proof of Concept
1. A user places an order via `IntentGatewayV2.placeOrder` with predispatch calldata that performs a multi-hop swap (e.g., ETH → WETH → intermediate token X → DAI), where the intermediate token X is not included in `order.inputs`.
2. Due to normal swap-path mechanics or partial slippage, a positive balance of token X remains on the `CallDispatcher` contract after `placeOrder` completes (the gateway only sweeps the DAI balance defined in `order.inputs`).
3. An unrelated attacker, monitoring the `CallDispatcher` address's token balances, calls `CallDispatcher.dispatch(abi.encode([Call({to: X, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, balanceOfX)})]))` directly.
4. Because `dispatch` has no access control, this call succeeds, transferring token X's balance to the attacker — funds that legitimately belonged to the gateway/user flow but were never re-custodied by an access-controlled contract.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L235-290)
```text
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;
                if (amount == 0) revert InvalidInput();

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    _sendValue(dispatcher, amount);
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }

            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);

            // Build sweep calls and snapshot gateway balances before the sweep.
            Call[] memory transferCalls = new Call[](inputsLen);
            uint256[] memory balancesBefore = new uint256[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;

                if (token == address(0)) {
                    uint256 balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                    balancesBefore[i] = address(this).balance;
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

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L86-98)
```text
## Calldata Execution

Both contracts support optional calldata execution on the destination chain via the `CallDispatcher`. By passing a non-empty `data` field in `SendParams`, the sender can trigger arbitrary contract calls on the destination chain immediately after tokens are minted or unlocked. This enables composable cross-chain workflows like transfer-and-swap (e.g., bridge USDC then swap to WETH via UniswapV2), transfer-and-stake, or transfer-and-deposit into a lending protocol — all in a single cross-chain operation.

The `data` field is an ABI-encoded `Call[]` array, where each `Call` specifies a target contract, a native value to forward, and the calldata to execute. On the destination chain, the HFT contract mints or unlocks tokens to the `to` address, then forwards the entire `data` payload to the `CallDispatcher`, which executes each call sequentially. If the calls need to spend the bridged tokens (e.g., approve then swap), set `to` to the `CallDispatcher` address so tokens are delivered directly to it.

For code examples, see the [HyperFungibleToken](/developers/evm/hyper-fungible-token/hyper-fungible-token#calldata-execution) and [WrappedHyperFungibleToken](/developers/evm/hyper-fungible-token/wrapped-hyper-fungible-token#calldata-execution) pages.

### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
```
