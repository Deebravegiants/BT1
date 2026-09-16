### Title
Native-fee dispatch permanently reverts when `feeToken()` equals the WETH address used in the Uniswap V2 swap path - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()` build a two-hop Uniswap V2 swap path `[WETH, feeToken()]` whenever a caller pays with `msg.value`. If the configured `feeToken()` is ever the same address as the router's `WETH()` (e.g. a deployment that denominates fees in the wrapped native asset, or a misconfiguration during `HostManager`/host-params update), `path[0] == path[1]`, and `IUniswapV2Router02.swapETHForExactTokens` reverts with `UniswapV2Library: IDENTICAL_ADDRESSES` on every call. This is the same root-cause bug class as the reported "swap DAI for DAI" issue: a hard-coded two-token swap path with no same-token guard.

### Finding Description
In `dispatch(DispatchPost)`:
```solidity
if (msg.value > 0) {
    address[] memory path = new address[](2);
    address uniswapV2 = _hostParams.uniswapV2;
    path[0] = IUniswapV2Router02(uniswapV2).WETH();
    path[1] = feeToken();
    IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
        post.fee, path, address(this), block.timestamp
    );
}
``` [1](#0-0) 

The identical pattern is repeated for `dispatch(DispatchGet)`: [2](#0-1) 

and referenced generically for `fundRequest()` in the interface docs: [3](#0-2) 

None of these code paths check whether `feeToken()` is the same token as `IUniswapV2Router02(uniswapV2).WETH()` before constructing the swap path. Uniswap V2's router (via `UniswapV2Library.sortTokens`) reverts with `IDENTICAL_ADDRESSES` whenever the two tokens in a swap path are equal, exactly mirroring the "DAI for DAI" failure mode in the reported issue — a hard-coded swap between two tokens that can coincide is executed unconditionally.

This is reachable by any unprivileged caller: every ordinary user or app dispatching a POST/GET request with `msg.value` (native-token fee payment) hits this exact code, as does `HyperApp.quote()`/`dispatchWithFeeToken()` callers who choose the native-payment path documented in `docs/content/developers/evm/messaging/post-requests.mdx`: [4](#0-3) 

Whether `feeToken() == WETH` can actually occur in a live deployment is a configuration question I could not fully verify — `_hostParams.uniswapV2` and `feeToken()` are set via governance/host-manager parameter updates, and I did not find an explicit require statement in `EvmHost.sol` preventing `feeToken` from being set to the chain's wrapped-native address (my search for such a guard, e.g. `WETH()==`/`IDENTICAL_ADDRESSES` checks in `EvmHost.sol`, returned no matches). If such a state is reachable — either as a legitimate deployment choice (some chains use the wrapped native asset as the ISMP fee token) or via a parameter-update mistake — dispatch of every native-fee message would be **permanently and unconditionally bricked** for that state machine.

### Impact Explanation
If triggered, this breaks the core "dispatch a message" entry point for the native-payment path across `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()` — i.e., a route that becomes unable to deliver messages whenever a user chooses to pay the relayer/protocol fee in native token. Any HyperApp built on `dispatchWithFeeToken`'s sibling native-payment flow (`IDispatcher(host()).dispatch{value: msg.value}(post)`, per the `HyperApp`/docs guidance) would revert every time, effectively a full DoS of the native-fee dispatch surface for that host. This matches the "route unable to deliver messages" acceptance criterion.

### Likelihood Explanation
Likelihood depends entirely on whether `feeToken()` can be configured to equal `IUniswapV2Router02.WETH()` for a given deployment. This is plausible in two ways: (1) a state machine that intentionally denominates ISMP fees in the wrapped native asset (e.g., a chain without a native stablecoin), and (2) a host-parameter update (`HostManager`) that changes `uniswapV2` or `feeToken` independently, creating a transient or permanent mismatch. I was unable to confirm from the indexed code whether `EvmHost`/`HostManager` explicitly forbids this configuration; no same-token check exists in the swap-path construction itself, so the contract itself provides no protection regardless of how such a state arises.

### Recommendation
Before constructing the swap path in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, add a check that reverts clearly (or skips the swap and treats `msg.value` as an already-in-feeToken transfer) when `feeToken() == IUniswapV2Router02(uniswapV2).WETH()`, and additionally add a guard in the host-parameter update path (`HostManager`) that rejects configuring `feeToken` equal to the router's `WETH()` address, preventing this state from being reachable at all.

### Proof of Concept
1. Deploy/configure `EvmHost` such that `_hostParams.uniswapV2` is a Uniswap V2 router whose `WETH()` returns address `W`, and set `feeToken()` (via governance/`HostManager`) to also resolve to `W`.
2. Any unprivileged caller calls `dispatch(DispatchPost)` (or `dispatch(DispatchGet)`, or `fundRequest`) with `msg.value > 0`.
3. Inside `dispatch`, `path[0] = W` and `path[1] = feeToken() = W`, so `path[0] == path[1]`.
4. `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)` reverts with `UniswapV2Library: IDENTICAL_ADDRESSES`.
5. Every subsequent native-fee dispatch call reverts identically — the native-payment message-dispatch route is permanently unusable while this configuration persists. [1](#0-0)

### Citations

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

**File:** evm/src/core/EvmHost.sol (L974-985)
```text
    function dispatch(DispatchGet memory get) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                get.fee, path, address(this), block.timestamp
            );
        } else if (get.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), get.fee);
        }
```

**File:** sdk/packages/core/contracts/interfaces/IDispatcher.sol (L148-164)
```text
    /**
     * @dev Increase the relayer fee for a previously dispatched request.
     * This is provided for use only on pending requests, such that when they timeout,
     * the user can recover the entire relayer fee.
     *
     * @notice Payment can be made with either the native token or the IHost.feeToken.
     * If native tokens are supplied, it will perform a swap under the hood using the local uniswap router.
     * Will revert if enough native tokens are not provided.
     *
     * If no native tokens are provided then it will try to collect payment from the calling contract in
     * the IHost.feeToken.
     *
     * If called on an already delivered request, these funds will be seen as a donation to the hyperbridge protocol.
     * @param commitment - The request commitment
     * @param amount - The amount provided in `IHost.feeToken()`
     */
    function fundRequest(bytes32 commitment, uint256 amount) external payable;
```

**File:** docs/content/developers/evm/api/idispatcher.mdx (L130-159)
```text

**Payment:**
- **Native token** (`msg.value`): Automatically swapped to fee token via Uniswap
- **Fee token**: Transferred from caller (requires prior approval)

---

### dispatch(DispatchGet)

Dispatches a GET request to query state on another chain.

```solidity lineNumbers
function dispatch(DispatchGet memory request) 
    external 
    payable 
    returns (bytes32 commitment)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `request` | `DispatchGet` | The GET request struct |

| Returns | Type | Description |
|---------|------|-------------|
| `commitment` | `bytes32` | Request commitment hash for tracking |

**Payment:**
- **Native token** (`msg.value`): Automatically swapped to fee token via Uniswap
- **Fee token**: Transferred from caller (requires prior approval)

```
