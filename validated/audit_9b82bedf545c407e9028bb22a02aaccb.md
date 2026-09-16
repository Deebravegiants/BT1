### Title
Native-token fee payments price and swap against live Uniswap V2 spot reserves with no TWAP protection - ([File: sdk/packages/core/contracts/apps/HyperApp.sol], [File: evm/src/core/EvmHost.sol])

### Summary
`HyperApp.quote()` and the native-token dispatch path in `EvmHost` derive the protocol/relayer fee owed by calling Uniswap V2's `getAmountsIn`, which reads instantaneous pool reserves (the `slot0`-equivalent spot price for a V2 pool) rather than a time-weighted average. The docs explicitly acknowledge this is "vulnerable to sandwich attacks" for off-chain estimation, but `EvmHost` itself imports `IUniswapV2Router02` and performs the actual native→feeToken conversion at dispatch time using the same volatile, un-TWAP'd price.

### Finding Description
`HyperApp.quote(DispatchPost)` / `quote(DispatchGet)` compute the native-token cost of a fee by calling the configured Uniswap V2 router's `getAmountsIn` against the live pool reserves: [1](#0-0) 

The documentation flags this exact behavior as dangerous when invoked on-chain because `getAmountsIn` reflects the current spot price of the pool, which can be trivially skewed within the same block/transaction via a sandwich or flash-loan-funded swap: [2](#0-1) 

Despite this documented warning being aimed at frontend callers, `EvmHost.sol` — the core protocol contract that actually executes the native-token fee swap during dispatch — imports the same `IUniswapV2Router02` interface and relies on the identically volatile, spot-priced AMM quote to convert a user's native-token payment into the `feeToken` that funds relayer incentives: [3](#0-2) 

This mirrors the reported analog exactly: a spot AMM price (Uniswap `slot0`/reserve-derived price) is used directly for a security/economically-sensitive calculation instead of a manipulation-resistant TWAP oracle.

### Impact Explanation
Because the fee conversion uses the pool's instantaneous reserves with no time-weighting, an attacker can atomically manipulate the pool (e.g., via a large swap executed immediately before the victim's dispatch transaction within the same block, or a flash-loan-funded swap) to skew the native/feeToken exchange rate used by the Host. Depending on which side of `getAmountsIn` is affected, this can:
- Cause a user's `dispatch{value: msg.value}` call to convert to fewer feeToken units than intended, resulting in an under-funded relayer fee escrow. Since relayers are profit-driven and select messages based on adequate fees, an under-funded message risks becoming a **route unable to deliver messages**.
- Alternatively, force users to overpay in native token for the same nominal feeToken amount, extracting value from senders.

Both outcomes fall within the accepted impact classes (unsound fee/economic accounting leading to undeliverable messages, or economic loss to unprivileged senders).

### Likelihood Explanation
Any unprivileged caller dispatching a POST/GET request and paying in native token (a normal, permissionless, single-transaction user flow) is exposed. Exploitation only requires the ability to execute a large swap against the same Uniswap V2 pool in the same block as the victim's dispatch call — a standard sandwich/flash-loan primitive, requiring no privileged role, governance, or off-chain trust assumption. The severity is bounded by pool liquidity and slippage limits (if any) enforced by the Host, which I was not able to fully verify within the available tool budget — see "Uncertainty" below.

### Recommendation
Replace the direct `getAmountsIn`/spot-reserve based conversion with a TWAP-based price (e.g., a Uniswap V3 TWAP oracle, or a Chainlink-style oracle as already used elsewhere in the codebase, such as `SimplexPaymaster._getOraclePrice`, which enforces staleness checks). At minimum, add slippage/maximum-deviation guards around the on-chain swap execution in `EvmHost`, analogous to the `maxDeviationBps` price guard already implemented in the Simplex Uniswap V4 funding planner (`checkPriceGuard`), so a single-block price skew cannot silently under- or over-charge dispatch fees.

### Proof of Concept
Conceptual PoC (exact call sequence in `EvmHost`'s native-fee dispatch path could not be fully retrieved within the tool budget for this session):
1. Attacker identifies a pending dispatch transaction (or submits their own) that pays the Hyperbridge fee in native token via `IDispatcher(host).dispatch{value: msg.value}(post)`.
2. Attacker front-runs with a large swap against the same Uniswap V2 pool (WETH ⇄ feeToken) used by `EvmHost.uniswapV2Router()`, or funds the swap via flash loan, to skew reserves.
3. The victim's dispatch transaction executes `getAmountsIn`/the equivalent conversion against the now-skewed spot price, causing the resulting feeToken amount funding the relayer escrow to be less than intended for the given native `msg.value`.
4. Attacker reverses the swap (or the arbitrage naturally reverts pool state), pocketing the price impact while leaving the dispatched message under-funded.

**Uncertainty**: I was unable to retrieve and confirm the specific `EvmHost.sol` function body that performs the actual native→feeToken swap execution (including whether a slippage/deadline parameter or minimum-output check bounds the damage) before the tool budget was exhausted. The core claim — that fee-token conversion for native-token dispatch payments is anchored to a live, un-TWAP'd Uniswap V2 spot price via `getAmountsIn`, mirroring the reported `slot0` volatility issue — is supported by the imported `IUniswapV2Router02` interface in `EvmHost.sol` and by the `HyperApp.quote()` implementation and its accompanying documentation warning. A full assessment of exploitability bounds (e.g., existing slippage caps) would require reviewing the complete dispatch/fee-collection logic in `EvmHost.sol`, which a Devin session with full repository access could confirm.

### Citations

**File:** sdk/packages/core/contracts/apps/HyperApp.sol (L73-92)
```text
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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L236-238)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>
```

**File:** evm/src/core/EvmHost.sol (L38-38)
```text
import {IUniswapV2Router02} from "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";
```
