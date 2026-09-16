### Title
Chainlink price feeds in `SimplexPaymaster` lack an L2 sequencer-uptime check - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster._getOraclePrice` consumes Chainlink `AggregatorV3Interface.latestRoundData()` and only enforces an `updatedAt` staleness bound (`maxOracleAge`), with no check of a Chainlink L2 sequencer-uptime feed. The paymaster's documented deployment targets include Optimism, Base and Arbitrum (Base/Ethereum stablecoins with staleness bound "up to 24h" per the comment), all rollups where Chainlink explicitly recommends gating price consumption on `SequencerUptimeFeed`.

### Finding Description
`_getOraclePrice` is the sole gate on oracle freshness/validity: [1](#0-0) 

It checks `answer > 0` and `block.timestamp - updatedAt <= maxOracleAge`, but never queries or validates against a sequencer-uptime oracle. This function backs both the per-UserOp gas pricing path (`_tokenPrice`, called from validation/postOp) and the treasury's `swapAndDeposit` minimum-output calculation: [2](#0-1) [3](#0-2) 

On an OP-Stack/Arbitrum rollup, `block.timestamp` (and block production generally) stalls while the sequencer is down, so a Chainlink round can remain within the `maxOracleAge` staleness window purely because no blocks have elapsed — the staleness check gives no protection during the outage. When the sequencer resumes, transactions execute in a burst before the Chainlink oracle round catches up to the true market price, so the on-chain answer can materially diverge from the fair price for a window, exactly as described in Chainlink's L2 sequencer-feed guidance referenced in the external report. `Params.maxOracleAge` is set at up to `MAX_ORACLE_AGE = 7 days`, further widening this window: [4](#0-3) [5](#0-4) 

### Impact Explanation
Any permissionless caller (a UserOp sender using this paymaster) can pay gas at a price derived from a stale-relative-to-market oracle answer during a sequencer-down/recovery window, extracting value from the paymaster's markup/treasury or forcing the paymaster to accept insufficient token payment for the gas it fronts. The treasury-only `swapAndDeposit` path is less directly attacker-controlled (gated to `treasury`), but the per-UserOp pricing path (`_tokenPrice` via `_erc20Cost`) is reachable by any unprivileged UserOp sender in a single transaction, and mispricing directly affects the paymaster's ERC-20/native asset holdings — a fund-drain vector consistent with Medium severity.

### Likelihood Explanation
Requires the L2 sequencer to actually go down/restart (an infrequent but real, historically observed event on OP-Stack and Arbitrum) and an attacker (or opportunistic user) to submit a UserOp during the narrow divergence window immediately following recovery. Likelihood is therefore conditional on sequencer outages, consistent with Medium.

### Recommendation
Add a Chainlink `SequencerUptimeFeed` check (per-chain address, mirroring `nativeOracle`/`tokenOracle` configuration) in `_getOraclePrice`: revert if the feed reports the sequencer as down, or if it has been up for less than Chainlink's recommended grace period (typically 1 hour) since the last `startedAt` transition, before trusting `latestRoundData()` for pricing.

### Proof of Concept
1. Deploy `SimplexPaymaster` on an OP-Stack/Arbitrum chain with `maxOracleAge` set generously (e.g. near `MAX_ORACLE_AGE`).
2. Simulate sequencer downtime (no new L2 blocks/timestamp advance) while the Chainlink price of the priced token moves materially off-chain.
3. On sequencer recovery, immediately submit a UserOp using the affected token for gas payment; `_getOraclePrice` returns the pre-outage `latestRoundData()` answer (still within `maxOracleAge`), and `_tokenPrice`/`estimateTokenCost` price the operation using this stale, market-diverged answer, since the code at lines 662-676 has no sequencer-liveness gate.

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

**File:** evm/src/utils/SimplexPaymaster.sol (L163-166)
```text

    /// @dev Hard ceiling on the governance-configurable oracle staleness bound.
    uint256 public constant MAX_ORACLE_AGE = 7 days;

```

**File:** evm/src/utils/SimplexPaymaster.sol (L462-467)
```text
        if (amountIn == 0 || amountIn > balance) amountIn = balance;

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
