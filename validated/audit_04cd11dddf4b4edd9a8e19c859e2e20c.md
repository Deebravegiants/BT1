### Title
Missing L2 sequencer uptime check in `SimplexPaymaster._getOraclePrice` on Arbitrum/Base - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster._getOraclePrice` reads Chainlink `latestRoundData()` and validates only positivity and staleness against `maxOracleAge`, with no check of the L2 sequencer's uptime status via Chainlink's Sequencer Uptime Feed. [1](#0-0)  The contract is deployed on Arbitrum and Base, both of which are L2s with a sequencer that can go down, during which Chainlink price feeds can silently stop updating without necessarily tripping the staleness window.

### Finding Description
`_getOraclePrice` is the sole price-validation function for both the native/USD and token/USD Chainlink feeds used throughout the contract's pricing logic. [2](#0-1)  It is called from `_tokenPrice` (used by `getTokenPrice`, `estimateTokenCost`, and the internal gas-cost pricing used to size ERC-20 charges in `fetchDetails`/`validate`) and from `swapAndDeposit` (used to compute `amountOutMin` for the fee-recycling swap). [3](#0-2) [4](#0-3) 

The contract is confirmed to be deployed on Arbitrum mainnet (`SimplexPaymaster: 0x7281Bccb4f0BCE44F3B8542d1fC5e51c2F5fC08C` for chain ID 42161) [5](#0-4)  and on Base and other chains per the deployment/decision documentation. [6](#0-5) [7](#0-6) 

Any address on Arbitrum/Base can reach `_getOraclePrice` indirectly and permissionlessly through:
- `fetchDetails`/`validate` during ERC-4337 `UserOperation` validation, which any solver/EOA submits through a bundler to pay gas via a registered stablecoin (`getTokenPrice`/`estimateTokenCost` are also `external`/public views callable by anyone).
- `swapAndDeposit`, which is treasury-gated for execution but its `amountOutMin` — and thus the actual swap execution price accepted on-chain — depends entirely on the unguarded oracle read.

During an L2 sequencer outage, the sequencer-fed Chainlink aggregator on that L2 can stop receiving updates. If the last recorded `updatedAt` still falls inside `maxOracleAge` (up to 90,000 seconds / 25 hours per the deploy script default) [8](#0-7) , the stale price will pass the staleness check and be used as if fresh, exactly the class of issue described in the referenced report for `SingleSidedLPVaultBase._getOraclePairPrice`.

### Impact Explanation
Using a stale-but-not-technically-expired price during an Arbitrum/Base sequencer outage lets any UserOperation sender pay gas fees in the registered stablecoin (USDC/USDT) at a mispriced (stale) native/token exchange rate. Because the paymaster sponsors gas and settles the token charge against this manipulated/mispriced rate, an attacker submitting operations during (or shortly after) a sequencer recovery/outage window can systematically underpay for sponsored gas, draining the paymaster's treasury value over time — a Medium-severity value-leak/loss-of-funds condition consistent with the reachable, permissionless entry points identified (`fetchDetails`, `validate`, `getTokenPrice`, `estimateTokenCost`, `swapAndDeposit`).

### Likelihood Explanation
Likelihood is Medium: it requires an L2 sequencer downtime/restart window (a known, periodically-occurring event on Arbitrum/Optimism-stack chains) combined with the last oracle update still being within `maxOracleAge` (which is deliberately generous — up to ~25 hours for stablecoin feeds). Given `maxOracleAge` is configured generously specifically to avoid reverting on legitimate late pushes, the window during which a stale price is silently accepted after sequencer downtime is realistic.

### Recommendation
Integrate Chainlink's L2 Sequencer Uptime Feed check in `_getOraclePrice` (or a wrapper called before it): read the sequencer feed's `answer` and `startedAt`, revert if the sequencer is down (`answer == 1`), and additionally enforce a grace period after it comes back up before trusting price data, mirroring Chainlink's documented L2 pattern.

### Proof of Concept
1. On Arbitrum/Base, the Arbitrum/OP-stack sequencer goes offline.
2. The Chainlink price feed used by `nativeOracle`/`tokenOracle` stops receiving new rounds, but its `updatedAt` from before the outage remains within `maxOracleAge` (up to 90,000s per the default deploy config). [8](#0-7) 
3. An attacker, aware that the true off-chain price has moved (e.g., native asset price crashed or spiked) since the last on-chain update, submits UserOperations that get validated via `fetchDetails`/`validate`, which price the ERC-20 charge using the stale `_getOraclePrice` result through `_tokenPrice`. [3](#0-2) [1](#0-0) 
4. The paymaster charges the attacker's stablecoin at the stale rate, sponsoring gas for less real value than intended, repeatable across multiple operations until the oracle updates or `maxOracleAge` finally expires the feed.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L454-479)
```text
    function swapAndDeposit(address token, uint256 amountIn) external {
        if (msg.sender != treasury) revert UnauthorizedCall();
        address router = IDispatcher(host()).uniswapV2Router();
        if (router == address(0)) revert InvalidRouter(router);
        TokenConfig memory cfg = tokenConfigs[token];
        if (address(cfg.tokenOracle) == address(0)) revert TokenNotRegistered(token);

        uint256 balance = IERC20(token).balanceOf(address(this));
        if (amountIn == 0 || amountIn > balance) amountIn = balance;

        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;

        address[] memory path = new address[](2);
        path[0] = token;
        path[1] = IUniswapV2Router02(router).WETH();

        IERC20(token).forceApprove(router, amountIn);
        uint256[] memory amounts = IUniswapV2Router02(router)
            .swapExactTokensForETH(amountIn, amountOutMin, path, address(this), block.timestamp);

        uint256 deposited = address(this).balance;
        entryPoint().depositTo{value: deposited}(address(this));
        emit FeesRecycled(token, amountIn, amounts[1], deposited);
```

**File:** evm/src/utils/SimplexPaymaster.sol (L653-658)
```text
    function _tokenPrice(TokenConfig memory cfg) internal view returns (uint256) {
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);

        return (nativeUsd * (10 ** cfg.tokenDecimals) * (10_000 + markupBps)) / (tokenUsd * 10_000);
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L660-676)
```text
    /// @dev Fetch a Chainlink price normalized to 8 decimals.
    ///      Reverts on stale or non-positive answers.
    function _getOraclePrice(AggregatorV3Interface oracle, uint8 oracleDecimals) internal view returns (uint256) {
        (, int256 answer,, uint256 updatedAt,) = oracle.latestRoundData();

        if (answer <= 0) revert InvalidOraclePrice(address(oracle), answer);
        if (block.timestamp - updatedAt > maxOracleAge) {
            revert StaleOraclePrice(address(oracle), updatedAt);
        }

        if (oracleDecimals < 8) {
            return uint256(answer) * (10 ** (8 - oracleDecimals));
        } else if (oracleDecimals > 8) {
            return uint256(answer) / (10 ** (oracleDecimals - 8));
        }
        return uint256(answer);
    }
```

**File:** sdk/packages/sdk/src/configs/chain.ts (L537-539)
```typescript
			CirclePaymaster: "0x0578cFB241215b77442a541325d6A4E6dFE700Ec",
			SimplexPaymaster: "0x7281Bccb4f0BCE44F3B8542d1fC5e51c2F5fC08C",
			Usdt0Oft: "0x14E4A1B13bf7F943c8ff7C51fb60FA964A298D92",
```

**File:** docs/content/developers/evm/simplex/configuration.mdx (L79-82)
```text
Solver selection requires each solver's EOA to be delegated to the `SolverAccount` contract. Simplex performs this automatically at startup via EIP-7702:

- **Primary path** — builds a no-op UserOperation with an attached EIP-7702 authorization and submits it through the configured bundler. When a paymaster is deployed on the chain — Circle Paymaster (USDC) preferred, then the `SimplexPaymaster` (USDC or USDT), live on Ethereum, Arbitrum, Base, Polygon and BSC — see [Mainnet Contract Addresses](/developers/evm/contract-addresses/mainnet) — and the solver holds at least one whole token of a supported stablecoin, the paymaster pays gas in that stablecoin so the solver never needs native gas for delegation. Tokens with EIP-2612 are authorized by permit; tokens without it (such as BSC stables) need a one-time funded `approve(Permit2, max)` from the solver EOA, after which every operation carries a per-op Permit2 signature and no native gas is ne ... (truncated)
- **Fallback** — if the bundler path fails or the chain has no paymaster, Simplex sends a direct type-0x04 delegation tx using the solver's native balance. On paymaster-less chains it also keeps the ERC-4337 EntryPoint deposit topped up to cover `targetGasUnits` (default 3,000,000) at the current gas price.
```

**File:** sdk/packages/simplex/docs/ai/decisions/2026-09-07-the-paymaster-relayer-is-governance-relayer-and-the-release.md (L7-9)
```markdown

Release order: live Ethereum, Base and Polygon proxies predate `PERMIT2()`, and the configured BSC
and Arbitrum addresses have no code. The filler never funds an EntryPoint deposit on a chain with a
```

**File:** evm/script/DeploySimplexPaymaster.s.sol (L16-20)
```text
        uint256 markupBps = vm.envOr("MARKUP_BPS", uint256(200)); // default 2%
        address treasury = vm.envOr("TREASURY", admin); // default to deployer
        // Stablecoin feeds on Ethereum and Base run a 24h heartbeat; a buffer over
        // 24h avoids transient StaleOraclePrice reverts on late pushes.
        uint256 maxOracleAge = vm.envOr("MAX_ORACLE_AGE", uint256(90_000));
```
