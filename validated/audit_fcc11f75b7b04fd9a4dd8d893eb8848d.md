Now I have sufficient evidence to confirm the analog. The `CallDispatcher` is a **single shared singleton** across `HyperFungibleToken`, `WrappedHyperFungibleToken`, and `IntentGatewayV2` (same deployed address on every chain, per `docs/content/developers/evm/contract-addresses/mainnet.mdx`), and its `dispatch()` function has **no caller restriction whatsoever** — this is the "weak sandbox" analog to CVE-2020-27605 (an untrusted-content executor with no isolation).

### Title
Unrestricted `CallDispatcher.dispatch()` allows theft of any funds transiently held by the shared dispatcher during cross-app calldata execution - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch()` is `external` with **no access control** (no `onlyHost`, no caller allowlist), yet the contract is designed to transiently hold user/protocol funds (native ETH and ERC20 tokens) while executing attacker/solver-supplied `Call[]` during `HyperFungibleToken`, `WrappedHyperFungibleToken`, and `IntentGatewayV2` predispatch/postdispatch flows. This is the same class of flaw as CVE-2020-27605: an execution sandbox around untrusted, attacker-controlled operations that provides no isolation boundary.

### Finding Description
`CallDispatcher` is deployed once and shared as `_params.dispatcher` by every app on a chain [1](#0-0) . Its only entry point has zero caller checks: [2](#0-1) 

Multiple flows route real value through this same address before the calls execute:
- `IntentGatewayV2.placeOrder` sends predispatch assets (native ETH via `_sendValue`/raw `.call`, or ERC20 via `safeTransferFrom`) directly to `dispatcher`, then calls `dispatch(order.predispatch.call)` with **solver/user-supplied** call data, then sweeps the result back [3](#0-2) .
- `IntentsBase._execute` sends output tokens to the same `dispatcher`, dispatches attacker-influenced `order.output.call`, then sweeps residual balances [4](#0-3) .
- `HyperFungibleToken.onAccept` / `WrappedHyperFungibleToken.onAccept` mint or unlock tokens directly to the dispatcher address (`to = CALL_DISPATCHER`) before calling `ICallDispatcher(_dispatcher).dispatch(message.data)` [5](#0-4) [6](#0-5) .

Because `dispatch()` has no restriction, any external account can invoke it directly, at any time, on the exact same shared address that all three apps use to stage funds mid-flow. The dispatcher's own `receive()` accepts ETH from anyone unconditionally [7](#0-6) , and documentation confirms the dispatcher is expected to "hold and forward native tokens" and hold tokens "temporarily during execution" across all these flows [8](#0-7) [9](#0-8) .

### Impact Explanation
Because the same `CallDispatcher` address is shared across `IntentGatewayV2`, `HyperFungibleToken`, and `WrappedHyperFungibleToken`, and any dust, unswept balance, or ETH sent by mistake/self-destruct/force-send accumulates there permanently until claimed, an unrestricted `dispatch()` lets **any address** sweep out that balance via `Call{to: attacker, value: balance}` or an ERC20 `transfer` to itself. This is a direct theft of funds that belong to the protocol/users (e.g., "dust" the intent-gateway docs explicitly say is meant to be swept to a protocol treasury via governance, not to an arbitrary caller) [10](#0-9) .

### Likelihood Explanation
High for the dust-theft path — no privileged role, no valid intent, no signature needed; a bot merely needs to call `dispatch()` whenever the dispatcher accrues a nonzero balance (native ETH is trivially force-sendable via `receive()`, and ERC20 dust can appear from fee-on-transfer tokens, rounding, or partially executed batches). The atomic same-block interception of an in-flight order's transient balance is not reachable, but persistent balances the dispatcher accumulates between transactions are.

### Recommendation
Restrict `CallDispatcher.dispatch()` to a caller allowlist (the registered `IntentGatewayV2`, `HyperFungibleToken`, `WrappedHyperFungibleToken` addresses, or a single trusted host/relayer), or deploy a dedicated dispatcher instance per app so cross-app fund co-mingling cannot occur, and add a permissioned sweep function for any residual balance instead of leaving `dispatch()` open to arbitrary sweeps.

### Proof of Concept
1. Force-send ETH to the shared `CallDispatcher` address (e.g. via a `selfdestruct` from a throwaway contract, or simply exploit any transaction that leaves rounding dust as documented).
2. Call `CallDispatcher.dispatch(abi.encode([Call({to: attacker, value: dispatcher.balance, data: ""})]))` directly — no caller check exists in [11](#0-10)  to prevent this.
3. The dispatcher forwards its entire balance to the attacker.

### Citations

**File:** docs/content/developers/evm/contract-addresses/mainnet.mdx (L64-66)
```text
| `CallDispatcher` | [`0xE2C7e576E26E0bE7aC97c6fE925bcDAbD87c4bEd`](https://optimistic.etherscan.io/address/0xE2C7e576E26E0bE7aC97c6fE925bcDAbD87c4bEd) |
| `IntentGatewayV2` | [`0xAe041F7B0CB581876832830baeB6a2Aa2a3C9716`](https://optimistic.etherscan.io/address/0xAe041F7B0CB581876832830baeB6a2Aa2a3C9716) |
| `IntentGatewayV2 (Implementation)` | [`0x9d82B05156d0da273D66C5cCbDccef2b00EE06A7`](https://optimistic.etherscan.io/address/0x9d82B05156d0da273D66C5cCbDccef2b00EE06A7) |
```

**File:** evm/src/utils/CallDispatcher.sol (L36-61)
```text
    /**
     * @dev Receive function to accept ETH transfers
     */
    receive() external payable {}

    /**
     *  @dev reverts if the target is not a contract or if any of the calls reverts.
     */
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

**File:** evm/src/apps/IntentGatewayV2.sol (L234-258)
```text
        uint256 msgValue = msg.value;
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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-502)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L299-305)
```text
        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L299-328)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        HyperFungibleToken.Message memory message = abi.decode(request.body, (HyperFungibleToken.Message));
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
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-97)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

```

**File:** docs/content/developers/evm/hyper-fungible-token/wrapped-hyper-fungible-token.mdx (L164-176)
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
```

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L83-83)
```text
Protocol fees are retained as "dust" in the gateway and can be swept to a treasury via Hyperbridge governance. When a solver provides more tokens than required, the excess is split according to `surplusShareBps` (100% to protocol if the order has calldata). Surplus only applies on the first fill of each output token pair.
```
