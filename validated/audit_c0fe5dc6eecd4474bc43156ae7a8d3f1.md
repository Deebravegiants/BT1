## Analysis: Single-AMM price oracle used for Hyperbridge message-dispatch fee conversion

The reported issue (`SwapperImpl.sol` relying on one oracle source) maps onto a concrete pattern in `EvmHost.sol`: every native-token-funded dispatch path prices the ETH→feeToken conversion from a single Uniswap V2 pool with no manipulation resistance, staleness check, or secondary source.### Title
`EvmHost` prices native-token dispatch fees from a single unprotected Uniswap V2 pool, exposing message dispatch to sandwich manipulation and forced reverts - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest` all convert a caller's native-token payment into `feeToken` by calling `swapETHForExactTokens` against exactly one configured Uniswap V2 pool (`_hostParams.uniswapV2`). There is no TWAP, no secondary price source, no maximum-deviation check, and no explicit refund step for the caller — the same "single centralized oracle source" anti-pattern flagged in the external `SwapperImpl.sol` report, here applied to the core message-dispatch fee path rather than a swapper.

### Finding Description
In `dispatch(DispatchPost memory post)`: [1](#0-0) 

the exact same unguarded pattern is repeated in `dispatch(DispatchGet)` and `fundRequest`, both calling `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(...)` with `path[0] = WETH`, `path[1] = feeToken()`, i.e. the instantaneous spot price of one on-chain pool is the sole exchange-rate authority used to determine how much native token is consumed for a caller-specified `feeToken` amount. [2](#0-1) [3](#0-2) 

The project's own documentation acknowledges this exact class of risk for the read-only `quote()` helper built on the same router (`IUniswapV2Router02(_uniswap).getAmountsIn`), explicitly warning it is "vulnerable to sandwich attacks" and should never be called on-chain: [4](#0-3) 

Yet `EvmHost.dispatch`/`fundRequest` perform the analogous on-chain swap unconditionally whenever `msg.value > 0`, with no slippage bound other than the caller's own `msg.value`, and no protection against the pool being sandwiched in the same transaction bundle as the dispatch call. `_hostParams.uniswapV2` is a single governance-set address (`HostParams.uniswapV2`) with no fallback oracle, no TWAP, and no price-deviation guard: [5](#0-4) 

This mirrors the reported bug class precisely: reliance on a single, unauthenticated, spot-priced market as the "oracle" for a critical protocol accounting operation (fee collection that gates message dispatch), instead of a manipulation-resistant or multi-source design.

### Impact Explanation
Any unprivileged account can front-run/back-run a victim's `dispatch{value: ...}(...)` (or `fundRequest`) call to move the WETH/feeToken price in the single Uniswap V2 pool:
- **Forced dispatch failure (route unable to deliver messages):** by pushing the price against the victim, the attacker can make the pool require more input than the victim's supplied `msg.value` covers `post.fee`, causing `swapETHForExactTokens` to revert and the entire dispatch (and thus the cross-chain message) to fail — a griefing vector against any app's message dispatch that relies on native-token payment.
- **Value extraction from dispatchers:** because the swap is executed at the manipulated spot price with no minimum-output/maximum-slippage guard tied to a trusted reference price, an attacker can classically sandwich the trade, extracting value from users/apps paying dispatch fees in native token across every EVM deployment of `EvmHost`.

Since dispatch is the entry point for essentially all outbound ISMP POST/GET requests paid in native token, this affects a foundational, frequently-used path rather than a peripheral feature.

### Likelihood Explanation
Every `dispatch{value:...}` or `fundRequest{value:...}` call is exposed each time it executes, since the vulnerable code path is unconditional whenever `msg.value > 0` — no opt-out, no guard. Uniswap V2 pools are public and manipulable by any actor with sufficient capital or a flash loan, and MEV searchers routinely monitor mempools for exactly this kind of unprotected AMM interaction. The barrier to exploitation is low; it requires no special privilege, only observing pending dispatch transactions that pay with native token.

### Recommendation
- Do not rely solely on the live Uniswap V2 spot price for a fee-critical on-chain conversion. Bound the swap with a maximum-slippage parameter validated against a manipulation-resistant reference (e.g., a TWAP over the same pool, or a Chainlink feed cross-check as already used elsewhere in the codebase, e.g. `SimplexPaymaster.sol`'s `_getOraclePrice`).
- Alternatively, require callers to always pay `feeToken` directly (already supported) and deprecate/guard the native-token auto-swap path, or add an explicit `amountInMax`/deadline plus a sanity check against a secondary price source before calling `swapETHForExactTokens`.
- Ensure any leftover native value from the swap is explicitly refunded to `_msgSender()`, since the router refunds unspent ETH to `address(this)` (the Host), not to the original caller.

### Proof of Concept
1. Attacker observes a pending `EvmHost.dispatch{value: v}(DispatchPost{fee: F, ...})` transaction in the mempool, where `v` is sized against the current pool price to net exactly `F` feeToken via `swapETHForExactTokens`.
2. Attacker front-runs with a large WETH→feeToken swap on the same Uniswap V2 pool (`_hostParams.uniswapV2`), moving the price so that acquiring `F` feeToken now costs more than `v` wei.
3. The victim's `dispatch` call reverts inside `swapETHForExactTokens` (insufficient `msg.value`), causing the intended cross-chain message dispatch to fail entirely — or, if the attacker instead sizes the manipulation to stay just under `v`, they capture the sandwich profit at the victim's expense.
4. Attacker back-runs to restore the pool price, completing the sandwich and either griefing the dispatch (DoS) or extracting value, all without any privileged access — reachable by any address able to submit a transaction ahead of a public `dispatch()`/`fundRequest()` call.

### Citations

**File:** evm/src/core/EvmHost.sol (L40-56)
```text
// The EvmHost protocol parameters
struct HostParams {
    // The fee token contract address. This will typically be DAI.
    // but we allow it to be configurable to prevent future regrets.
    address feeToken;
    // The admin account, this only has the rights to freeze, or unfreeze the bridge
    address admin;
    // Ismp message handler contract. This performs all verification logic
    // needed to validate cross-chain messages before they are dispatched to local modules
    address handler;
    // The authorized host manager contract, is itself an `IApp`
    // which receives governance requests from the Hyperbridge chain to either
    // withdraw revenue from the host or update its protocol parameters
    address hostManager;
    // The local UniswapV2Router02 contract, used for swapping the native token to the feeToken.
    address uniswapV2;
    // The unstaking period of Polkadot's validators. In order to prevent long-range attacks
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

**File:** sdk/packages/core/contracts/apps/HyperApp.sol (L70-80)
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
```
