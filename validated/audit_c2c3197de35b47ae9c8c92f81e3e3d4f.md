### Title
Shared `maxOracleAge` staleness bound applied to Chainlink price feeds with materially different heartbeats in `SimplexPaymaster._getOraclePrice()` - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster` prices ERC-4337 gas payments using two independent Chainlink feeds — `nativeOracle` (native asset/USD) and each token's `tokenOracle` (token/USD) — but checks both feeds' `updatedAt` timestamps against the exact same governance-configured `maxOracleAge` bound, even though the contract's own documentation acknowledges Chainlink heartbeats vary drastically by feed/chain.

### Finding Description
`_getOraclePrice()` reverts with `StaleOraclePrice` only if `block.timestamp - updatedAt > maxOracleAge`, using one shared `maxOracleAge` for every oracle call: [1](#0-0) 

This single bound is used for both the native asset oracle and the token oracle, as seen in `_tokenPrice()`: [2](#0-1) 

The contract's own NatSpec documents that these feeds have wildly different heartbeats — "BSC stablecoins ~27s, Base/Ethereum stablecoins up to 24h" — yet `Params.maxOracleAge` is a single value validated only against a hard ceiling of `MAX_ORACLE_AGE = 7 days`: [3](#0-2) [4](#0-3) 

This is the same bug class as the referenced `ChainLinkOraclePivot._getLatestRoundData()` report: two Chainlink feeds with individualized deviation-threshold/heartbeat configurations are checked against one shared staleness delta, so a bound fitted for one feed is wrong for the other.

### Impact Explanation
If governance sets `maxOracleAge` loose enough to tolerate a long-heartbeat token feed (e.g. close to 24h, within the `7 days` hard cap), a short-heartbeat `nativeOracle` (e.g. ~27s on BSC) that stalls or is manipulated/stale can silently continue to be accepted for up to that same long window. Because `_tokenPrice()`/`_getOraclePrice()` feeds directly into `tokenPrice`, `_fetchDetails`, and `_prefund`, an attacker able to submit UserOps (any unprivileged bundler/user) during a native-asset price divergence window can systematically underpay for gas relative to the true native-asset cost, draining the paymaster's ERC-20 surplus/EntryPoint deposit over repeated operations — a form of theft of protocol funds. Conversely, a bound tightened for the short-heartbeat feed causes the long-heartbeat token feed to revert `StaleOraclePrice` far more often than its actual reporting cadence justifies, denying legitimate users the ability to pay gas with that token (a freezing/DoS effect on that payment path).

### Likelihood Explanation
Reachable by any unprivileged actor: no special permission is needed to submit a UserOp that triggers `_fetchDetails`/`_prefund`/`_getOraclePrice`, and `swapAndDeposit` also calls both oracles via the shared bound. Only governance sets `maxOracleAge`, but the contract's own docs concede heartbeats differ per token/chain, meaning any single value that is safe for one feed is provably unsafe for the other — the mis-parameterization is not a hypothetical, it is baked into the deployment reality described in the NatSpec.

### Recommendation
Store staleness bounds per-oracle instead of one contract-wide `maxOracleAge`: add a `maxAge` field to `TokenConfig` and to the native oracle configuration, validate each against `MAX_ORACLE_AGE`, and use the feed-specific value in `_getOraclePrice()` for both the native and token legs of every price computation.

### Proof of Concept
1. Governance calls `UpdateParams` (via `onAccept`) with `maxOracleAge` set to, e.g., 20 hours, to accommodate a registered stablecoin whose Chainlink feed heartbeat is ~24h (per `RegisterToken`).
2. The `nativeOracle` (e.g., BNB/USD with a ~27s heartbeat) stops updating due to an outage or is delayed.
3. For up to the full 20-hour window, `_getOraclePrice(nativeOracle, ...)` in `_tokenPrice()` does not revert (`block.timestamp - updatedAt <= maxOracleAge`), so stale/incorrect native price data continues to be used to compute `tokenPrice`.
4. During a period where the real native asset price has moved significantly from the stale reported price, any user submits UserOps priced via `_fetchDetails`/`_prefund`, paying the paymaster based on the stale rate.
5. Repeated over many operations, this systematically mispriced conversion drains the paymaster's accumulated ERC-20 surplus/EntryPoint deposit relative to actual gas cost, while `_getOraclePrice`'s single shared bound gives no independent protection against the native feed's much shorter expected heartbeat.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L139-152)
```text
    struct Params {
        /// @notice Native asset / USD oracle (BNB/USD on BSC, ETH/USD on Ethereum, etc.)
        AggregatorV3Interface nativeOracle;
        /// @notice Markup in basis points (100 = 1%). Applied on top of the oracle price.
        uint256 markupBps;
        /// @notice Receives markup surplus and EntryPoint deposit withdrawals.
        address treasury;
        /// @notice Maximum oracle staleness. Chainlink heartbeats vary per chain
        ///         (BSC stablecoins ~27s, Base/Ethereum stablecoins up to 24h).
        uint256 maxOracleAge;
        /// @notice Slippage tolerance in basis points applied to the
        ///         oracle-derived expected output in {swapAndDeposit}.
        uint256 swapSlippageBps;
    }
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
