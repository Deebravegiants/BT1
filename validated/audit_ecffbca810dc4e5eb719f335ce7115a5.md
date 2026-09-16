Found the analog. The docs explicitly flag this: `HyperApp.quote()` is documented as "vulnerable to sandwich attacks" and "**Do not call `quote()` in smart contract transactions**" [1](#0-0) , but this is a documentation-only mitigation with no on-chain enforcement — a dispatching app or an end user relying on `HyperApp.quote()` off-chain still has no protection at execution time.

### Title
Native-fee dispatch has no slippage bound between `quote()` and `dispatch()`, letting a sandwiched swap overpay or exceed budget with no refund path - (File: `sdk/packages/core/contracts/apps/HyperApp.sol`, `evm/src/core/EvmHost.sol`)

### Summary
`HyperApp.quote(DispatchPost)` / `quote(DispatchGet)` compute the native-token amount needed to buy `request.fee` units of the fee token via `IUniswapV2Router02.getAmountsIn`, read live from the Uniswap V2 pool reserves at call time [2](#0-1) . The caller then submits a separate transaction, `dispatch{value: msg.value}(request)` on `EvmHost`, which performs `swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)` [3](#0-2) . This mirrors the reported bug class: an amount previewed from mutable AMM state at one point in time is consumed in a later transaction whose actual on-chain state can differ, with no bound parameter tying the two together.

### Finding Description
`EvmHost.dispatch(DispatchPost)`/`dispatch(DispatchGet)` require exactly `post.fee` (or `get.fee`) units of the fee token, obtained via `swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)` [3](#0-2) [4](#0-3) . Because it is `swapETHForExactTokens`, the router will consume up to `msg.value` of ETH; the deadline is `block.timestamp` (i.e., "any time this tx mines" — no real staleness bound), and the router itself reverts only if `msg.value` is insufficient (`InsufficientInputAmount`), but does not otherwise cap what a manipulated pool takes.

The value sent as `msg.value` is derived off-chain from `HyperApp.quote()`, which reads `getAmountsIn(request.fee, path)` against the pool's reserves at call time [5](#0-4) . There is no `maxNativeIn`/slippage-bound parameter passed through `dispatch()`, `dispatchWithFeeToken()`, or any `HyperApp` sender function — the only enforced invariant is "provide at least enough ETH to buy `post.fee` fee-tokens at the router's live price," which the caller cannot know precisely by the time their transaction executes. An attacker who front-runs (or simply the natural drift of the AMM reserves between the `quote()` call and the `dispatch` transaction landing) can move the WETH/feeToken pool price so that:
- the quoted `msg.value` is now insufficient, causing the whole dispatch (and any surrounding app logic that assumed dispatch would succeed) to revert; or
- if the caller pads `msg.value` generously to avoid reverts, the excess ETH beyond what `swapETHForExactTokens` consumes is refunded by the router to the Host contract (`address(this)` = Host), not to the original caller — the Host does not appear to forward any router refund back to `_msgSender()`/`post.payer` in the code shown, meaning any ETH the router refunds after a favorable/adversarial price move is not returned to the app or user who submitted it.

This applies to every unprivileged path that dispatches a POST/GET request paying with native token: any relayer, app, intent solver, or bandwidth purchaser calling `IDispatcher.dispatch{value: ...}(...)` directly (as shown in the SDK docs pattern) is exposed [6](#0-5) .

### Impact Explanation
- A user/app that pays the exact quoted `msg.value` can have their dispatch revert due to price movement between quote-time and execution-time, since `EvmHost.dispatch` performs no fallback and no partial-payment path — the whole message dispatch fails and must be resubmitted, delaying cross-chain messages (a liveness/availability issue for the messaging pipeline).
- A user/app that pads `msg.value` to be safe against slippage risks losing the unspent portion: `swapETHForExactTokens` refunds unused ETH to the caller of the swap, which is the `EvmHost` contract itself, not to `_msgSender()` of `dispatch()`. Unless `EvmHost` explicitly forwards this refund back to the payer (not shown in the reviewed code), the excess native token sent by the app/user is permanently stranded in the Host contract — a direct loss of user funds triggered entirely by ordinary AMM price movement or a griefing sandwich, with no way for the payer to recover it.
- This directly matches the reported bug class ("value computed from mutable state is stale by execution time, and the caller absorbs the difference with no bound/refund guarantee") applied to Hyperbridge's own fee-payment rail used by every native-fee dispatcher, relayer-funding call (`fundRequest`), and third-party HyperApp integrator.

### Likelihood Explanation
Every unprivileged caller who pays dispatch fees in native token exercises this path; Uniswap V2 pools for WETH/feeToken are public and can be moved by anyone with a swap in the same or an adjacent block. The documentation's own warning ("vulnerable to sandwich attacks... only use it off-chain") confirms the maintainers are aware `quote()` is unreliable at execution time, and no on-chain bound was added to `dispatch()` to compensate — so exploitation requires no special access, just ordinary MEV/sandwiching or natural market movement, and is expected to occur routinely rather than as a rare edge case.

### Recommendation
- Add an explicit slippage/bound parameter (e.g., `uint256 maxNativeIn` or a `deadline` tied to actual expiry rather than `block.timestamp`) to `dispatch(DispatchPost)`/`dispatch(DispatchGet)`/`fundRequest`, and pass it through to `swapETHForExactTokens` in place of the unbounded default, reverting cleanly if the price has moved past the caller's tolerance.
- Ensure any native token the Uniswap router refunds after `swapETHForExactTokens` is forwarded back to `_msgSender()` (or `post.payer`) rather than retained by `EvmHost`, and add a test asserting the caller's ETH balance is correctly reconciled after dispatch.
- Consider deprecating or clearly gating the on-chain-callable `HyperApp.quote()` (e.g., marking it `view`-incompatible or restricting to off-chain `eth_call` usage only) since it currently returns a non-`view` value that can be invoked mid-transaction and mistaken for a safe on-chain price oracle.

### Proof of Concept
1. App/user calls `HyperApp.quote(post)` off-chain, obtaining `nativeCost` from `getAmountsIn(post.fee, [WETH, feeToken])` at the pool's current reserves [7](#0-6) .
2. Attacker observes the pending `dispatch{value: nativeCost}(post)` transaction in the mempool and front-runs it with a large swap that shifts the WETH/feeToken pool price against the payer's quoted rate.
3. The victim's transaction executes `EvmHost.dispatch`, calling `swapETHForExactTokens{value: nativeCost}(post.fee, path, address(this), block.timestamp)` [8](#0-7) .
   - If `nativeCost` is now insufficient to buy `post.fee` fee-tokens, the router reverts the entire dispatch (denial of service on that message).
   - If the payer had padded `nativeCost` for safety and the swap now needs less ETH than provided, the router refunds the difference to `address(this)` (the Host) rather than to the original payer, and that ETH is not observed to be forwarded back in the reviewed `dispatch` implementation — resulting in a stuck/lost refund for the payer.
4. Attacker back-runs to restore the pool price, pocketing the price-movement profit (classic sandwich) while the victim either loses gas on a reverted dispatch or loses the unrefunded native-token excess.

**Note on uncertainty:** I could not fully confirm within the reviewed snippets whether `EvmHost` forwards any Uniswap-router ETH refund back to `_msgSender()`/`post.payer` elsewhere in the contract (e.g., via a `receive()`/fallback sweep at end of `dispatch`) — this is the pivotal detail determining whether the impact is "wasted gas + revert" (denial of service) or "permanent loss of native funds" (a stronger, funds-at-risk finding). Given index size limits, the full `EvmHost.sol` contract body was not entirely visible; a Devin session with full repository access should verify this specific refund-handling behavior before finalizing severity.

### Citations

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L162-189)
```text
### Native Token Payment

For native token payments, dispatch directly and let the Host handle the Uniswap swap:

```solidity lineNumbers title="MyApp.sol"
contract MyApp is HyperApp {
    function sendMessageWithNative(
        bytes memory message,
        bytes memory dest,
        uint64 timeout,
        address to,
        uint256 relayerFee
    ) public payable returns (bytes32) {
        DispatchPost memory post = DispatchPost({
            body: message,
            dest: dest,
            timeout: timeout,
            to: abi.encode(to),
            fee: relayerFee,
            payer: msg.sender
        });
        
        // User must send enough native tokens to cover fees
        // The Host will swap native -> feeToken via Uniswap
        return IDispatcher(host()).dispatch{value: msg.value}(post);
    }
}
```
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L236-238)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>
```

**File:** sdk/packages/core/contracts/apps/HyperApp.sol (L70-92)
```text
    /**
     * @dev returns the quoted fee in the native token for dispatching a POST request
     */
    function quote(DispatchPost memory request) public returns (uint256) {
        address _host = host();
        address _uniswap = IDispatcher(_host).uniswapV2Router();
        address[] memory path = new address[](2);
        path[0] = IUniswapV2Router02(_uniswap).WETH();
        path[1] = IDispatcher(_host).feeToken();
        return IUniswapV2Router02(_uniswap).getAmountsIn(request.fee, path)[0];
    }

    /**
     * @dev returns the quoted fee in the native token for dispatching a GET request
     */
    function quote(DispatchGet memory request) public returns (uint256) {
        address _host = host();
        address _uniswap = IDispatcher(_host).uniswapV2Router();
        address[] memory path = new address[](2);
        path[0] = IUniswapV2Router02(_uniswap).WETH();
        path[1] = IDispatcher(_host).feeToken();
        return IUniswapV2Router02(_uniswap).getAmountsIn(request.fee, path)[0];
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
