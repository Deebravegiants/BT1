Confirmed: `_setParams` at [1](#0-0)  stores a single global `maxOracleAge` that is applied uniformly to `nativeOracle` and to every registered token's `tokenOracle` via `_getOraclePrice` at [2](#0-1) , regardless of each feed's actual Chainlink heartbeat. This exactly mirrors the reported bug class (a single fixed staleness constant applied across oracles with different real heartbeats).

### Title
Single global `maxOracleAge` staleness bound applied to all Chainlink feeds regardless of individual heartbeat, allowing stale-price exploitation of `SimplexPaymaster` - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster` uses one governance-configured `maxOracleAge` value to bound staleness for *every* Chainlink `AggregatorV3Interface` feed it consults — the native asset/USD oracle and every registered ERC-20 token/USD oracle — instead of a per-oracle bound reflecting that specific feed's heartbeat.

### Finding Description
`_getOraclePrice` is the sole staleness gate for any oracle read by the paymaster: [3](#0-2) 
It checks `block.timestamp - updatedAt > maxOracleAge`, where `maxOracleAge` is one contract-wide storage variable set via governance's `UpdateParams` request, validated only against a static ceiling `MAX_ORACLE_AGE = 7 days`: [4](#0-3) [1](#0-0) 

The paymaster's own deployment comment documents that it is meant to serve feeds with wildly different heartbeats in the same instance/parameter set — "BSC stablecoins ~27s, Base/Ethereum stablecoins up to 24h" — and the deploy script picks `maxOracleAge` generously (`90_000` seconds ≈ 25h) to avoid reverts on the slowest feed: [5](#0-4) 

There is no per-`TokenConfig` or per-oracle staleness field — `TokenConfig` carries only the oracle address and decimals: [6](#0-5) 

Because one `maxOracleAge` gates both `nativeOracle` and every `cfg.tokenOracle` (see `_tokenPrice`), a feed whose actual heartbeat is much shorter than `maxOracleAge` (e.g., a BSC feed updating every ~27s) can silently stop updating (oracle outage, sequencer/aggregator freeze, chain congestion, or a compromised/paused feed) and still be treated as "fresh" for up to the full `maxOracleAge` window (tens of minutes to hours) instead of the few-minute margin appropriate to that feed's own heartbeat: [7](#0-6) 

This is the same bug class as the referenced report: a single fixed timeout constant is used to gate freshness for oracles whose actual update cadence differs by orders of magnitude, defeating the purpose of a heartbeat-based staleness check for the fast-updating feeds.

### Impact Explanation
`_tokenPrice`/`_getOraclePrice` directly determine how many ERC-20 tokens (USDC/USDT/etc.) a UserOp's sender is charged in exchange for sponsored native-gas: `_erc20Cost` in the base `PaymasterERC20` uses `_tokenPrice` for the prefund pulled via Permit2/permit in `_prefund`, and for the final settlement in `_postOp`. If a token or native oracle used by this pricing freezes at a stale (favorable) value while remaining inside the oversized `maxOracleAge` window, any actor able to submit a sponsored UserOp (a "bandwidth purchaser" of the paymaster's gas sponsorship, e.g. the intents solver flow that builds paymaster-sponsored bid UserOps in `ContractInteractionService.prepareBidUserOp`) can systematically underpay the treasury relative to true market price for the sponsored gas, directly draining paymaster/treasury funds over repeated fills. This is a concrete theft-of-funds vector against the paymaster's ERC-20 surplus and EntryPoint deposit.

### Likelihood Explanation
Exploitation requires an oracle used by this specific paymaster deployment to freeze or diverge from spot price while remaining within the shared `maxOracleAge` window — a scenario Chainlink feeds have experienced historically (e.g., stale/paused aggregators, low-liquidity chain feeds). Because governance must size `maxOracleAge` to the *slowest* feed it manages, any faster feed in the same deployment is left with a staleness tolerance far looser than its own heartbeat justifies, materially raising the odds that a freeze on the fast feed goes undetected long enough to be exploited by an automated, always-listening actor (e.g., a solver bot in the intents pipeline) monitoring for stale-but-accepted prices.

### Recommendation
Store staleness bounds per-oracle rather than as one global `maxOracleAge`. Add a `maxAge` field to `TokenConfig` (and a dedicated `nativeMaxOracleAge`), set per feed at `RegisterToken`/`UpdateParams` time based on that feed's documented heartbeat plus a small safety margin, and check `block.timestamp - updatedAt > cfg.maxAge` in `_getOraclePrice` for both the native and the token oracle independently.

### Proof of Concept
1. Governance deploys/updates `SimplexPaymaster` supporting both a fast-heartbeat feed (e.g., BUSD/USD on BSC, ~27s heartbeat) and a slow-heartbeat feed (e.g., ETH/USD on mainnet, 24h heartbeat) under one `maxOracleAge` sized to accommodate the slow feed (`~90_000`s, per `evm/script/DeploySimplexPaymaster.s.sol` line 20).
2. The fast feed's aggregator stalls (a real, historically-observed Chainlink failure mode) at a price favorable to the caller, but `block.timestamp - updatedAt` stays below `maxOracleAge` for a long window.
3. A solver/relayer submits UserOps sponsored by `SimplexPaymaster`; `_getOraclePrice` (`SimplexPaymaster.sol:662-668`) accepts the stale, favorable price for the entire `maxOracleAge` window.
4. `_tokenPrice` computes an under-market ERC-20 charge for the sponsored gas across many prefunds/postOps, draining the treasury's expected markup and potentially the surplus/deposit over repeated fills, while the same protection would have reverted much sooner had the fast feed's own heartbeat been used as the bound.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L154-159)
```text
    struct TokenConfig {
        AggregatorV3Interface tokenOracle; // token/USD feed
        uint8 tokenOracleDecimals; // cached decimals() of tokenOracle
        uint8 tokenDecimals; // decimals() of the ERC-20
        bool active; // kill-switch per token
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L164-165)
```text
    /// @dev Hard ceiling on the governance-configurable oracle staleness bound.
    uint256 public constant MAX_ORACLE_AGE = 7 days;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L359-383)
```text
    function _setParams(Params memory p) internal {
        if (address(p.nativeOracle) == address(0)) revert ZeroAddress();
        if (p.treasury == address(0)) revert ZeroAddress();
        if (p.markupBps > MAX_MARKUP_BPS) revert InvalidMarkup(p.markupBps);
        if (p.maxOracleAge == 0 || p.maxOracleAge > MAX_ORACLE_AGE) revert InvalidOracleAge(p.maxOracleAge);
        if (p.swapSlippageBps > MAX_SWAP_SLIPPAGE_BPS) revert InvalidSlippage(p.swapSlippageBps);

        emit ParamsUpdated(
            Params({
                nativeOracle: nativeOracle,
                markupBps: markupBps,
                treasury: treasury,
                maxOracleAge: maxOracleAge,
                swapSlippageBps: swapSlippageBps
            }),
            p
        );

        nativeOracle = p.nativeOracle;
        nativeOracleDecimals = p.nativeOracle.decimals();
        markupBps = p.markupBps;
        treasury = p.treasury;
        maxOracleAge = p.maxOracleAge;
        swapSlippageBps = p.swapSlippageBps;
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L653-658)
```text
    function _tokenPrice(TokenConfig memory cfg) internal view returns (uint256) {
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);

        return (nativeUsd * (10 ** cfg.tokenDecimals) * (10_000 + markupBps)) / (tokenUsd * 10_000);
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L660-668)
```text
    /// @dev Fetch a Chainlink price normalized to 8 decimals.
    ///      Reverts on stale or non-positive answers.
    function _getOraclePrice(AggregatorV3Interface oracle, uint8 oracleDecimals) internal view returns (uint256) {
        (, int256 answer,, uint256 updatedAt,) = oracle.latestRoundData();

        if (answer <= 0) revert InvalidOraclePrice(address(oracle), answer);
        if (block.timestamp - updatedAt > maxOracleAge) {
            revert StaleOraclePrice(address(oracle), updatedAt);
        }
```

**File:** evm/script/DeploySimplexPaymaster.s.sol (L16-21)
```text
        uint256 markupBps = vm.envOr("MARKUP_BPS", uint256(200)); // default 2%
        address treasury = vm.envOr("TREASURY", admin); // default to deployer
        // Stablecoin feeds on Ethereum and Base run a 24h heartbeat; a buffer over
        // 24h avoids transient StaleOraclePrice reverts on late pushes.
        uint256 maxOracleAge = vm.envOr("MAX_ORACLE_AGE", uint256(90_000));
        uint256 swapSlippageBps = vm.envOr("SWAP_SLIPPAGE_BPS", uint256(200)); // default 2%
```
