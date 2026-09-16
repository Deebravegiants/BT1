### Title
`EvmHost.dispatch()`/`fundRequest()` force native-fee payers through a single hardcoded UniswapV2 router with no user-controlled slippage/path, and strand refund dust in the host contract - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()` accept native ETH from any caller and internally force a fee-token swap through one hardcoded router (`_hostParams.uniswapV2`) using a hardcoded two-hop path `[WETH, feeToken]`, exactly mirroring the reported bug class of a swap module that "requires users to swap all tokens through same router and hardcoded paths." Because these are unprivileged, directly reachable dispatch entry points for every ISMP request originator, any pricing/liquidity flaw in that single router/path is imposed on every user with no ability to choose a better route or set independent slippage protection.

### Finding Description
In `evm/src/core/EvmHost.sol`, dispatching a POST or GET request (or funding one) with `msg.value > 0` always routes through the same fixed router and fixed path: [1](#0-0) [2](#0-1) 

The path and router are hardcoded/governance-set, not user-selectable: [3](#0-2) 

The call uses `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)`. In UniswapV2Router02's standard implementation, this function refunds any leftover ETH (`msg.value - amountIn`) to `msg.sender` of the swap call — which, here, is `EvmHost` itself, not the original end-user calling `dispatch()`/`fundRequest()`. Any ETH sent above the exact amount required to acquire `post.fee`/`amount` of `feeToken` is therefore refunded into the `EvmHost` contract balance rather than back to the caller who supplied it. There is no code path in `dispatch()`/`fundRequest()` that forwards or accounts for this native-ETH dust back to `_msgSender()`; the only way ETH is ever removed from `EvmHost` is via the strictly governance/hostManager-gated `withdraw()` function: [4](#0-3) 

Since `dispatch()`/`fundRequest()` are unprivileged, permissionless entry points invoked by ordinary users/apps paying fees natively, and the exact ETH amount required by the pool at execution time is unknown to the caller ahead of time (pool price can move between quote and execution due to normal trading or MEV), essentially any caller who doesn't send the *exact* minimal `amountIn` loses the difference permanently to the protocol, with no self-service recovery mechanism.

The same hardcoded-router/no-slippage-control pattern recurs in `SimplexPaymaster.swapAndDeposit()` and the SDK's `TokenGateway.convertNativeToFeeToken()`, but those are either treasury-gated or off-chain estimation only, so `EvmHost.dispatch()`/`fundRequest()` is the strongest unprivileged, directly-reachable analog.

### Impact Explanation
Every native-fee-paying user of `dispatch()`/`fundRequest()` is forced to lose any ETH sent beyond the exact swap input required, since the refund lands in `EvmHost`'s own balance instead of returning to the payer. This is a direct, repeatable loss of user funds (native tokens) on the single most common entry point into the ISMP dispatch pipeline, not merely a griefing/DoS: the excess is not returned to the user and can only ever be moved by governance via `withdraw()`, to an arbitrary beneficiary chosen by governance, not the original overpaying user. This qualifies as a concrete freezing/loss-of-funds issue for the impacted (unprivileged) callers, consistent with Medium severity for the underlying bug class (forced swap through a single hardcoded router/path with no minOut/refund guarantees to the caller).

### Likelihood Explanation
High likelihood in practice: any caller sending native ETH to `dispatch()`/`fundRequest()` who cannot precisely predict the exact `amountIn` UniswapV2 will require at execution time (due to normal price drift, gas estimation buffers, or standard "send a little extra to be safe" behavior) will overpay and lose the difference. This requires no attacker at all — it is triggered by routine, honest usage of the standard entry points that every EVM app/relayer/user integrates with to pay ISMP dispatch fees natively.

### Recommendation
- Refund unused native ETH from the swap back to `_msgSender()` (or the designated payer) instead of leaving it in `EvmHost`, by tracking the ETH balance delta around the router call and forwarding any leftover to the caller.
- Alternatively, replace the fixed exact-output swap against a hardcoded path/router with a caller-supplied minimum output/maximum input and permit passing an alternate router/path (or an off-chain-quoted calldata blob executed via a restricted swap adapter), so users are not solely exposed to one router/pool's liquidity and pricing.
- Add an explicit test asserting that ETH dust from `dispatch()`/`fundRequest()` swaps is returned to the caller, not retained by the host contract.

### Proof of Concept
1. Deploy `EvmHost` with `_hostParams.uniswapV2` pointed at a real UniswapV2Router02 and a WETH/feeToken pool.
2. As an arbitrary user, call `dispatch(DispatchPost{ ..., fee: F })` with `msg.value = M` where `M` is slightly larger than the exact ETH required to obtain `F` fee tokens at the current pool price (a realistic scenario since the caller cannot know the precise on-chain price at execution time).
3. Internally, `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: M}(F, [WETH, feeToken], address(this), block.timestamp)` executes; UniswapV2Router02 computes `amountIn < M`, performs the swap, and refunds `M - amountIn` ETH to `msg.sender`, which is `EvmHost`, not the calling user.
4. Observe that the user's balance decreased by the full `M`, while `EvmHost`'s native ETH balance increased by `M - amountIn`; the user has no function to reclaim this delta — only `withdraw()`, gated by `restrict(_hostParams.hostManager)`, can move it, and only to a beneficiary chosen through cross-chain governance. [1](#0-0) [2](#0-1) [5](#0-4)

### Citations

**File:** evm/src/core/EvmHost.sol (L54-55)
```text
    // The local UniswapV2Router02 contract, used for swapping the native token to the feeToken.
    address uniswapV2;
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

**File:** evm/src/core/EvmHost.sol (L1031-1042)
```text
    function fundRequest(bytes32 commitment, uint256 amount) external payable notFrozen {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                amount, path, address(this), block.timestamp
            );
        } else {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), amount);
        }
```
