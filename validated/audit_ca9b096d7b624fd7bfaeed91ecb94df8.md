### Title
`HyperbridgeLzEndpoint.send()` lets any caller drain the adapter's pooled feeToken balance, causing dispatch failures for all OApps routed through it - (File: `sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol`)

### Summary
`HyperbridgeLzEndpoint` is a permissionless LayerZero-compatible adapter that routes messages through Hyperbridge's ISMP `dispatch()`. When an OApp pays in the fee token (rather than native), `send()` assumes the fee token was already transferred to the adapter contract by the caller's `_payLzToken` flow, then approves the entire current feeToken balance of the adapter to the host and calls `dispatch()` with no value. Because `send()` has no caller/OApp allowlist (only `whenNotPaused`), and `EvmHost.dispatch()` pulls `post.fee` via `safeTransferFrom(_msgSender(), ...)` where `_msgSender()` is the adapter contract itself (not the original `send()` caller), any address can invoke `send()` and have the fee silently paid out of whatever feeToken balance currently sits in the adapter — including the residual buffer left over from other OApps' overpayments.

### Finding Description
In `send()`: [1](#0-0) 
when `msg.value == 0`, the code comments explicitly assume "Fee tokens already transferred to this contract by OFT's `_payLzToken`" and then does:
```
IERC20(feeToken).forceApprove(_host, IERC20(feeToken).balanceOf(address(this)));
IDispatcher(_host).dispatch(request);
```
This approves and exposes the adapter's *entire current* feeToken balance to the host for the dispatch, not just funds attributable to the current caller. `quote()` deliberately quotes callers 2x the relayer fee as a buffer for legacy per-byte host fees: [2](#0-1) 
so under normal operation, each legitimate `_payLzToken`-driven call leaves unused excess feeToken sitting in the adapter contract's balance — a shared, unowned pool.

`send()` itself is not restricted to a known/authorized OApp — its only modifier is `whenNotPaused`: [3](#0-2) 
So any address can call `send()` directly with `msg.value == 0` and no prior feeToken transfer of its own. In that case, `dispatch()` on `EvmHost` collects `post.fee` via `_msgSender()`, which resolves to the `HyperbridgeLzEndpoint` contract (the caller of `dispatch`), not the original EOA that invoked `send()`: [4](#0-3) 
The fee is therefore taken out of the adapter's shared balance rather than from the actual `send()` caller.

An attacker can repeatedly call `send()` with dummy messages and `msg.value = 0`, each time consuming `relayerFee(dstEid)` from the adapter's pooled feeToken balance (built up from other OApps' 2x-buffer overpayments) without contributing any tokens themselves. This is directly analogous to the reported LayerZero `CrossChainRouter._send` bug: a shared balance meant to fund cross-chain messaging fees for legitimate protocol operations can be drained by unrelated, permissionless, low-cost calls.

### Impact Explanation
Once the adapter's feeToken balance is exhausted, subsequent legitimate `send()` calls from real OApps that rely on the buffer (or even calls that transferred exactly the relayer fee but land after the attacker's drain) will fail: `dispatch()`'s `safeTransferFrom` reverts on insufficient balance, since `EvmHost.dispatch()` transfers `post.fee` from the adapter's own balance. This DOSes the entire LayerZero-to-Hyperbridge bridging route for every OApp built on top of `HyperbridgeLzEndpoint` — a "route unable to deliver messages" condition — until the adapter's balance is manually replenished (e.g., by the owner or another paying OApp), causing message delivery delays/failures for all downstream OFTs/OApps using this endpoint.

### Likelihood Explanation
The attack requires only calling a public, unauthenticated function (`send()`) with `msg.value = 0` and an arbitrary destination/message — no privileged role, no governance, and minimal gas cost per call relative to the fee drained. Any dust of buffer balance accumulated from legitimate traffic is immediately exploitable, and the attack can be repeated continuously to keep the adapter's balance near zero, making it a persistent, low-cost DOS vector once any residual balance exists.

### Recommendation
`send()` should collect the exact fee required for the specific message from `msg.sender` (or from the calling OApp) at call time — e.g., via `safeTransferFrom(msg.sender, address(this), relayerFee(dstEid))` before approving/dispatching — rather than relying on and exposing whatever balance happens to be sitting in the adapter contract. Alternatively, track fee token credits per-OApp/per-message so `dispatch()` only ever spends funds attributable to the specific call being processed, eliminating the shared, drainable pool.

### Proof of Concept
1. Legitimate OApp A calls `quote()` for a message to `dstEid`, receives `lzTokenFee = relayerFee(dstEid) * 2`, transfers that amount of feeToken to `HyperbridgeLzEndpoint` via its `_payLzToken` flow, then calls `send()`. `dispatch()` consumes only `relayerFee(dstEid)`, leaving `relayerFee(dstEid)` as residual balance in the adapter.
2. Attacker calls `send()` directly (any `MessagingParams`, `msg.value = 0`) without transferring any feeToken to the adapter.
3. `send()` approves the adapter's full current feeToken balance (including OApp A's residual) to the host and calls `dispatch()`, which pulls `relayerFee(dstEid)` from that balance — paid for by OApp A's leftover funds, not the attacker.
4. Attacker repeats step 2/3 until the adapter's feeToken balance is fully drained.
5. The next legitimate `send()` call that depends on the buffer (or arrives with a marginal balance) fails at `EvmHost.dispatch()`'s `safeTransferFrom` due to insufficient balance, blocking message delivery for that OApp/chain pair.

### Citations

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L261-266)
```text
    /// @inheritdoc ILayerZeroEndpointV2
    function send(
        MessagingParams calldata _params,
        address /* _refundAddress */
    ) external payable override whenNotPaused returns (MessagingReceipt memory) {
        bytes memory dest = _eidToStateMachine[_params.dstEid];
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L296-306)
```text
        if (msg.value > 0) {
            IDispatcher(_host).dispatch{value: msg.value}(request);
        } else {
            // Fee tokens already transferred to this contract by OFT's _payLzToken.
            // The quoted lzTokenFee includes a buffer above the relayer fee so the
            // legacy deployed host's per-byte protocol fee can be paid out of it;
            // approve our full feeToken balance and let the host take what it needs.
            address feeToken = IDispatcher(_host).feeToken();
            IERC20(feeToken).forceApprove(_host, IERC20(feeToken).balanceOf(address(this)));
            IDispatcher(_host).dispatch(request);
        }
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L337-345)
```text
        // Apply a generous 2x buffer to absorb the legacy deployed host's
        // per-byte protocol fee (the in-source host has no such markup). Excess
        // native is refunded by the uniswap router; excess feeToken approval is
        // simply unused.
        if (_params.payInLzToken) {
            return MessagingFee({nativeFee: 0, lzTokenFee: request.fee * 2});
        } else {
            return MessagingFee({nativeFee: quote(request) * 2, lzTokenFee: 0});
        }
```

**File:** evm/src/core/EvmHost.sol (L921-932)
```text
    function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                post.fee, path, address(this), block.timestamp
            );
        } else if (post.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), post.fee);
        }
```
