### Title
`SimplexPaymaster::_getOraclePrice` prices gas on Chainlink feeds with no L2 sequencer-uptime check - ([File: evm/src/utils/SimplexPaymaster.sol])

### Summary
`SimplexPaymaster` prices ERC-20 gas payments purely from `AggregatorV3Interface.latestRoundData()`, validating only that the answer is positive and that `updatedAt` is within `maxOracleAge`. It never checks an L2 sequencer-uptime feed (e.g. Chainlink's `0xBCF85224fc0756B9Fa45aA7892530B47e10b6433` on Arbitrum). This is deployed on Base/BSC/Ethereum per the contract's own docs, and Base is an OP-stack L2 subject to sequencer downtime, so the bug class from the external report (staleness check bypassed by a resuming sequencer) is directly reachable here.

### Finding Description
`_getOraclePrice` is the sole gate on price freshness for both the native/USD and token/USD legs used to price every UserOp's gas prefund: [1](#0-0) 

It checks `answer > 0` and `block.timestamp - updatedAt <= maxOracleAge`, but never queries an L2 sequencer-uptime feed. On OP-stack/Arbitrum-style L2s, when the sequencer goes down, the last round's `updatedAt` freezes; but once the sequencer restarts, the aggregator can post a "fresh" round whose `updatedAt` clears the staleness check while the price itself reflects a market that moved during the outage (or, per Chainlink's L2 guidance, a round can be reported with a recent timestamp immediately after sequencer resumption despite the underlying data being effectively stale/unverified during the interim). Any unprivileged caller can trigger this pricing path simply by submitting a sponsored UserOp through the paymaster (`_prefund` → `_tokenPrice` → `_getOraclePrice`), which is the entry point invoked on every gas-sponsored UserOp: [2](#0-1) 

The contract's own header documents deployment across BSC, Base, and Ethereum, with Base being an OP-stack L2 exposed to sequencer outages: [3](#0-2) 

A repository-wide search confirms there is no sequencer-uptime feed check anywhere in the codebase (`grep_search` for `sequencer|Sequencer` only returned Arbitrum Orbit/BEEFY consensus code, unrelated to Chainlink price feeds), and the same unguarded Chainlink-only pattern is repeated in `swapAndDeposit`, which also derives its slippage-protected minimum output straight from `_getOraclePrice`: [4](#0-3) 

### Impact Explanation
An unprivileged UserOp submitter (any sender able to construct paymasterData) can exploit a stale-but-"fresh-looking" price during/after an L2 sequencer outage to have gas priced far below (or above) fair value: underpricing lets attackers drain the paymaster's stablecoin surplus/entrypoint deposit relative to actual gas cost (protocol funds loss), while overpricing overcharges honest users. The same stale price also corrupts `swapAndDeposit`'s `amountOutMin`, letting a mispriced swap convert accrued fee tokens to native at an unfavorable rate, further threatening protocol solvency. This is a concrete loss-of-funds path reachable from a single unprivileged transaction (a sponsored UserOp), satisfying the Medium/High bar.

### Likelihood Explanation
L2 sequencer downtime is an infrequent but recurring, externally-observed event (Arbitrum and OP-stack chains have both experienced multi-hour outages). Exploitation requires no special privilege — any party able to submit a UserOp through the paymaster during/immediately after such an outage window can trigger mispriced gas. Given Base is explicitly one of the target deployment chains, likelihood is non-trivial but conditioned on an external sequencer-outage event, placing this at Medium likelihood.

### Recommendation
Integrate Chainlink's `L2SequencerUptimeFeed` per the officially documented pattern: query `latestRoundData()` on the sequencer-uptime feed for the target L2, revert if `answer == 1` (sequencer down), and additionally enforce a grace period after `startedAt` (e.g. Chainlink's recommended `GRACE_PERIOD_TIME`) before trusting any price feed again. Apply this check inside `_getOraclePrice` (and any other price-dependent path such as `swapAndDeposit`) for all L2 deployments (Base et al.), gating price usage on sequencer liveness in addition to the existing staleness/positivity checks.

### Proof of Concept
1. Deploy `SimplexPaymaster` on Base (OP-stack L2) with `nativeOracle`/`tokenOracle` set to the real Chainlink ETH/USD and USDC/USD feeds; `maxOracleAge` set to the feed's normal heartbeat (e.g. 3600s).
2. Simulate a sequencer outage: freeze the L2 block/timestamp advance while the Chainlink off-chain reporters cannot post updates (aggregator `updatedAt` stalls).
3. Upon sequencer resumption, the aggregator posts a new round whose `updatedAt` is recent (passes `block.timestamp - updatedAt <= maxOracleAge`) but whose `answer` reflects a price that diverged materially from the true market price during the outage window (verifiable off-chain via a reference price source at that timestamp).
4. Immediately submit a UserOp with `paymasterData` referencing the mispriced token; `_prefund` → `_tokenPrice` → `_getOraclePrice` accepts the stale-but-fresh-looking answer and prices the required token prefund using the divergent rate, allowing the caller to pay far less token value than actual gas cost — directly matching `_getOraclePrice`'s check at `evm/src/utils/SimplexPaymaster.sol:662-668`, which has no sequencer-liveness gate.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L140-148)
```text
        /// @notice Native asset / USD oracle (BNB/USD on BSC, ETH/USD on Ethereum, etc.)
        AggregatorV3Interface nativeOracle;
        /// @notice Markup in basis points (100 = 1%). Applied on top of the oracle price.
        uint256 markupBps;
        /// @notice Receives markup surplus and EntryPoint deposit withdrawals.
        address treasury;
        /// @notice Maximum oracle staleness. Chainlink heartbeats vary per chain
        ///         (BSC stablecoins ~27s, Base/Ethereum stablecoins up to 24h).
        uint256 maxOracleAge;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L461-467)
```text
        uint256 balance = IERC20(token).balanceOf(address(this));
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
