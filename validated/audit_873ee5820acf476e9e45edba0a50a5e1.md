Confirmed: `_registerToken` (evm/src/utils/SimplexPaymaster.sol:387-404) registers each token's Chainlink oracle without any per-feed staleness threshold — only a single global `maxOracleAge` set via `_setParams` (evm/src/utils/SimplexPaymaster.sol:359-383) governs staleness for the native oracle and every registered ERC-20 token oracle. This applies the same freshness bound to feeds with materially different heartbeats (e.g., stablecoin/USD feeds with 1h heartbeats vs. others), which is the same bug class as the reported issue.

### Title
Single global `maxOracleAge` applied to all Chainlink price feeds regardless of per-feed heartbeat, enabling stale-price acceptance - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster` uses one governance-configurable `maxOracleAge` value to bound staleness for both the native/USD oracle and every registered ERC-20 token/USD oracle, instead of a per-feed threshold tuned to each Chainlink feed's actual heartbeat.

### Finding Description
`_registerToken` stores a `TokenConfig` per token containing only the oracle address and its decimals — no staleness threshold field: [1](#0-0) [2](#0-1) 

Staleness is enforced solely by the single `maxOracleAge` parameter, set once for the whole contract via `_setParams`/`UpdateParams`, and applied identically to `nativeOracle` and to every `cfg.tokenOracle` in `_getOraclePrice`: [3](#0-2) [4](#0-3) 

Chainlink feeds have different heartbeats depending on chain and asset (e.g., the contract's own comment notes "BSC stablecoins ~27s, Base/Ethereum stablecoins up to 24h"). Because `maxOracleAge` is a single value capped only by `MAX_ORACLE_AGE = 7 days`, governance is forced to either set it loose enough to accommodate the least-frequently-updated feed (accepting stale prices from tighter-heartbeat feeds for hours/days) or tight enough for the fastest feed (causing unrelated feeds with legitimately longer heartbeats to revert unnecessarily). There is no mechanism to assign each token's oracle its own staleness bound matching its real heartbeat, mirroring the reported bug class of a hardcoded/uniform staleness threshold applied across price feeds with different actual update cadences.

### Impact Explanation
`_getOraclePrice` gates both token pricing (`_tokenPrice`, used by `_validatePaymasterUserOp`/`_prefund` to size the ERC-20 prefund pulled from a solver) and fee-recycling swaps. If `maxOracleAge` is set to accommodate a slow-heartbeat token, a fast-heartbeat token's stale answer can still pass the check, causing the paymaster to price gas using an outdated USD rate — over- or under-charging the solver's ERC-20 prefund relative to the correct market rate, and similarly mispricing the minimum swap output derived from oracle prices during fee recycling (`_tokenPrice` minus `swapSlippageBps`). This is a paymaster/gas-accounting mispricing issue, not a total loss of funds, since exposure is further bounded by the signed Permit2/permit amount design already noted in the contract's own security-model comment.

### Likelihood Explanation
Any solver (an "intent solver" in the reachable-surface sense) building a bid `UserOp` through `prepareBidUserOp`/`buildSimplexPaymasterData` reaches this pricing path on every sponsored operation; no privileged action is required to trigger the mispricing — it only requires governance to have configured `maxOracleAge` per typical real-world Chainlink heartbeat mismatches (a plausible and likely-unnoticed misconfiguration, exactly as flagged in the original report).

### Recommendation
Store a per-token (and per-native-oracle) staleness threshold alongside the oracle address in `TokenConfig`/`Params`, set explicitly when a token or the native oracle is registered/updated (`RegisterToken`, `UpdateParams`), and validate it in `_getOraclePrice` against that feed's own threshold rather than one global `maxOracleAge`.

### Proof of Concept
1. Governance calls `UpdateParams` with `maxOracleAge` set to a value large enough to cover a token whose Chainlink feed has a genuinely long heartbeat (e.g., close to `MAX_ORACLE_AGE = 7 days`).
2. A second registered token (e.g., a stablecoin/USD feed with a 1-hour heartbeat) stops updating for several hours due to Chainlink deviation-threshold quiescence or feed disruption.
3. `_getOraclePrice` for that token still passes `block.timestamp - updatedAt > maxOracleAge` because the shared threshold is sized for the other token.
4. `_tokenPrice`/`_prefund` price the solver's UserOp gas cost using the stale answer, over- or under-charging relative to the true rate, until governance notices and re-registers the feed.

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

**File:** evm/src/utils/SimplexPaymaster.sol (L392-398)
```text
        tokenConfigs[token] = TokenConfig({
            tokenOracle: oracle,
            tokenOracleDecimals: oracle.decimals(),
            tokenDecimals: IERC20Metadata(token).decimals(),
            active: true
        });

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
