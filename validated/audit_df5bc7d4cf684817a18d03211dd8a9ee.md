### Title
Uniform `maxOracleAge` staleness bound applied to all Chainlink feeds regardless of per-feed heartbeat - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster` prices ERC-20 gas payments using Chainlink `AggregatorV3Interface` feeds for both the native asset and every registered ERC-20 token, and enforces staleness with a **single, protocol-wide** `maxOracleAge` value applied identically to every feed [1](#0-0) . Chainlink feed heartbeats vary widely per asset/chain (the contract's own comment cites BSC stablecoins ~27s vs. Base/Ethereum stablecoins up to 24h) [2](#0-1) , but there is no per-feed `customizedDelay`-style override — exactly the misconfiguration class described in the external Chainlink Oracle Misconfiguration report.

### Finding Description
`_getOraclePrice` reverts only if `block.timestamp - updatedAt > maxOracleAge`, where `maxOracleAge` is one governance-set value shared by `nativeOracle` and every `tokenConfigs[token].tokenOracle`: [3](#0-2) 

`maxOracleAge` is set once in `_setParams`, bounded only by `MAX_ORACLE_AGE = 7 days`, with no mechanism to configure a tighter/looser bound per token oracle: [4](#0-3) 

`_registerToken` likewise stores only the oracle address and its `decimals()`, never a per-token staleness bound: [5](#0-4) 

Both `_tokenPrice` (used for every UserOp's gas cost, `_fetchDetails`) and `swapAndDeposit` call `_getOraclePrice` with the same global `maxOracleAge` for the native oracle and the token oracle: [6](#0-5) [7](#0-6) 

Because a real deployment must register tokens/native assets whose Chainlink heartbeats differ by orders of magnitude (seconds vs. tens of thousands of seconds), governance is forced to either:
- set `maxOracleAge` tight (matching the fastest-heartbeat feed), causing `_getOraclePrice` to spuriously revert for any slower-heartbeat feed even when its price is legitimately fresh (denial of service on `_fetchDetails`/`getTokenPrice`/`estimateTokenCost` for that token), or
- set `maxOracleAge` loose (matching the slowest-heartbeat feed, up to the 7-day ceiling), which then lets a UserOp be priced using a native-asset or fast-heartbeat token price that is far more stale than its true heartbeat would ever normally allow.

### Impact Explanation
In the "loose" configuration, `_tokenPrice` can compute a UserOp's `erc20Cost` from a `nativeUsd`/`tokenUsd` pair that is stale far beyond the feed's actual update cadence. Any address able to submit a UserOp through this paymaster (an unprivileged bundler/user, i.e., a single submitted transaction) can time execution to a window where the stale cached price diverges materially from the live market price (e.g., after a native-asset price move that Chainlink has already reported on-chain via a fresher round the paymaster ignores, or during high volatility before the next heartbeat), causing the paymaster to charge the ERC-20-paying user less token than the gas is actually worth. This directly drains value from the paymaster's treasury/EntryPoint deposit over repeated exploitation — a concrete theft of funds from the protocol, reachable without any privileged role, mirroring the original report's warning that a uniform `acceptableDelay` "can result in the function operating with outdated data." In the "tight" configuration, legitimate `fetchDetails`/`getTokenPrice`/gas-payment flows for slower-heartbeat feeds revert unconditionally, denying service to a whole class of registered tokens.

### Likelihood Explanation
This is not a hypothetical: the contract's own NatSpec documents that BSC and Base/Ethereum stablecoin heartbeats differ by roughly three orders of magnitude, meaning any multi-token or multi-chain deployment intentionally covering both fast and slow feeds is forced into this trade-off by the current single-parameter design. No attacker privilege is required — a normal UserOp sender simply needs to submit at an opportune time, which is a passive, always-available exploitation strategy against a live paymaster serving normal traffic.

### Recommendation
Store a per-oracle (or per-token) staleness bound instead of one contract-wide `maxOracleAge`, analogous to the recommended `customizedDelay` mapping in the original report: extend `TokenConfig` (and the native-oracle params) with an explicit `maxAge` set at `RegisterToken`/`UpdateParams` time, validated against `MAX_ORACLE_AGE`, and have `_getOraclePrice` accept and enforce that feed-specific bound rather than the shared `maxOracleAge`.

### Proof of Concept
1. Governance registers a token whose Chainlink feed heartbeat is 24h (e.g., a Base/Ethereum-style stablecoin feed) alongside the native `BNB/USD` feed whose heartbeat is ~27s, and sets `maxOracleAge` to a value large enough to keep the 24h feed from spuriously reverting (e.g., `maxOracleAge = 1 days`), per `_setParams` in [4](#0-3) .
2. The native `BNB/USD` price moves materially (e.g., a 10%+ market move) but the on-chain `latestRoundData().updatedAt` for `nativeOracle` is, say, 12 hours old — well within `maxOracleAge` but far beyond the feed's true ~27s heartbeat.
3. Any user submits a UserOperation paying gas via the registered ERC-20 token. `_fetchDetails` → `_tokenPrice` → `_getOraclePrice` accepts the 12-hour-old native price without reverting (`block.timestamp - updatedAt (12h) <= maxOracleAge (1 day)`), per [8](#0-7) , computing `tokenPrice` from the stale, mispriced native/token ratio.
4. The user's ERC-20 payment (`_erc20Cost`) is charged based on the stale ratio, systematically under- or over-paying relative to the actual gas cost, extracting value from (or over-charging into) the paymaster treasury on every such UserOp submitted during the divergence window.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L145-148)
```text
        address treasury;
        /// @notice Maximum oracle staleness. Chainlink heartbeats vary per chain
        ///         (BSC stablecoins ~27s, Base/Ethereum stablecoins up to 24h).
        uint256 maxOracleAge;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L196-199)
```text
    AggregatorV3Interface public nativeOracle;
    uint8 public nativeOracleDecimals;
    uint256 public maxOracleAge;
    uint256 public markupBps;
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

**File:** evm/src/utils/SimplexPaymaster.sol (L387-404)
```text
    function _registerToken(address token, AggregatorV3Interface oracle) internal {
        if (token == address(0) || address(oracle) == address(0)) revert ZeroAddress();

        bool isNew = !tokenConfigs[token].active && address(tokenConfigs[token].tokenOracle) == address(0);

        tokenConfigs[token] = TokenConfig({
            tokenOracle: oracle,
            tokenOracleDecimals: oracle.decimals(),
            tokenDecimals: IERC20Metadata(token).decimals(),
            active: true
        });

        if (isNew) {
            registeredTokens.push(token);
        }

        emit TokenRegistered(token, address(oracle));
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L464-467)
```text
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;
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
