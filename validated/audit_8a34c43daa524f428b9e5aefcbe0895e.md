### Title
Unprotected AMM spot-price swap in `EvmHost` native fee payment lets an attacker manipulate the Uniswap V2 pool to trap victims' overpaid ETH in the contract - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest` all convert a caller's native token payment into `feeToken()` by calling the local Uniswap V2 router's `swapETHForExactTokens` directly against the pool's live reserves, with no TWAP, no minimum/maximum bound check beyond `msg.value`, and no forwarding of the router's excess-ETH refund back to the original caller. This is the same bug class as the HYDT exploit: an unprotected on-chain consumer trusts a manipulable Uniswap V2 spot price with no oracle safeguard.

### Finding Description
`dispatch(DispatchPost)` (and the analogous `dispatch(DispatchGet)` and `fundRequest`) do: [1](#0-0) 
```
if (msg.value > 0) {
    address[] memory path = new address[](2);
    address uniswapV2 = _hostParams.uniswapV2;
    path[0] = IUniswapV2Router02(uniswapV2).WETH();
    path[1] = feeToken();
    IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
        post.fee, path, address(this), block.timestamp
    );
}
```
`swapETHForExactTokens` computes the ETH required to obtain exactly `post.fee`/`amount` units of `feeToken()` purely from the pool's current reserves (spot price) at execution time — there is no TWAP, no `amountInMax` slippage guard distinct from the raw `msg.value`, and the recipient of any refunded (unused) ETH is `msg.sender` of the router call, which here is `EvmHost` itself, **not** the original transaction sender (`_msgSender()`/`tx.origin`). The docs for the same pattern in `HyperApp.quote()` explicitly warn that this pricing "uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks" and must only be used off-chain — yet the exact same unprotected spot-price mechanism is used **on-chain, synchronously, in the fund-moving path** of `dispatch`/`fundRequest`. [2](#0-1) 

Because the swap executes against the live pool state in the same transaction, an attacker can, in one atomic transaction (flash loan or their own large swap), push the WETH/feeToken pool price so that far less ETH than the true market rate is required to fill the fixed `feeToken` output (`post.fee`/`amount`). Any victim's `dispatch`/`fundRequest` call that follows in the same block (front-run/sandwich) — even one that sent an ETH amount sized off an honest off-chain `quote()` estimate with normal slippage buffer — will consume less ETH than expected in the manipulated swap, and the *entire unused remainder is refunded by the router to `EvmHost`'s own balance*, never returned to the caller. This differs from the intentional "excess = donation" comment that only covers the `feeToken` overpayment case in `fundRequest` doc comment (`If called on an already delivered request, these funds will be seen as a donation`); the ETH-refund-to-self happens unconditionally for every native-token payer, whether the request is known or not, and there is no accounting or withdrawal path in `EvmHost` for this trapped native ETH. [3](#0-2) 

### Impact Explanation
Every unprivileged caller who dispatches a POST/GET request or funds a request using native token payment (the standard, documented UX path) can have their ETH permanently siphoned into the `EvmHost` contract's un-withdrawable native balance by an attacker who manipulates the configured Uniswap V2 pool's spot price immediately before the victim's transaction executes. This is a direct, concrete freezing/loss of user funds triggered purely by price manipulation of an AMM the protocol treats as an oracle with no safeguard, reachable by any address (any relayer/dispatcher submitting a request), matching the report's "oracle price manipulation" bug class exactly (mintv2 trusting a manipulable pair price with no protection).

### Likelihood Explanation
High: manipulating a single Uniswap V2 pool's reserves via a flash-swap or large trade within one transaction/block is the exact, cheap, widely-demonstrated technique used in the referenced HYDT exploit. No privileged role is required — only a public relayer/dispatcher call plus a manipulable Uniswap V2 pool configured as `_hostParams.uniswapV2`, which is the documented, expected production configuration for native-fee payment.

### Recommendation
Do not perform on-chain swaps against the raw Uniswap V2 spot price for a security/fund-moving path. At minimum: (1) forward any refunded/unused native token back to `_msgSender()` after the swap instead of leaving it credited to `address(this)`; (2) bound the swap with a caller-specified `amountInMax` (rather than implicitly all of `msg.value`) so slippage/manipulation cannot silently consume more of the caller's value than intended; (3) consider a TWAP-based or otherwise manipulation-resistant price source for fee sizing, consistent with the project's own documentation warning against using spot-price `getAmountsIn` in any transaction context.

### Proof of Concept
1. Attacker takes a flash loan and performs a large swap on the `WETH/feeToken()` Uniswap V2 pool configured in `_hostParams.uniswapV2`, skewing reserves so that swapping WETH → feeToken yields far more feeToken per unit WETH than the honest market rate.
2. In the same block, front-run/sandwich a victim's `EvmHost.dispatch{value: X}(DispatchPost{...})` (or `fundRequest`) call, where `X` was sized off an honest off-chain `quote()`/`getAmountsIn()` estimate plus normal slippage buffer.
3. The victim's transaction executes `swapETHForExactTokens{value: X}(post.fee, [WETH, feeToken], address(this), block.timestamp)` against the manipulated pool; because feeToken is now "cheap" relative to WETH, only a small fraction of `X` is consumed, and the router refunds the remaining (large) unused ETH to `address(this)` — `EvmHost` — not to the victim.
4. Attacker reverses their flash-loan trade to restore the pool and repay the loan, keeping the AMM arbitrage profit; the victim's leftover ETH remains permanently stuck in `EvmHost`'s balance with no code path to reclaim or withdraw it. [4](#0-3)

### Citations

**File:** evm/src/core/EvmHost.sol (L921-959)
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

        // adjust the timeout
        uint64 timeoutTimestamp = post.timeout == 0 ? 0 : uint64(block.timestamp) + uint64(post.timeout);
        PostRequest memory request = PostRequest({
            source: host(),
            dest: post.dest,
            nonce: uint64(_nextNonce()),
            from: abi.encodePacked(_msgSender()),
            to: post.to,
            timeoutTimestamp: timeoutTimestamp,
            body: post.body
        });

        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee});
        emit PostRequestEvent({
            source: string(request.source),
            dest: string(request.dest),
            from: _msgSender(),
            to: abi.encodePacked(request.to),
            nonce: request.nonce,
            timeoutTimestamp: request.timeoutTimestamp,
            body: request.body,
            fee: post.fee
        });
    }
```

**File:** evm/src/core/EvmHost.sol (L1031-1040)
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
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L236-238)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>
```
