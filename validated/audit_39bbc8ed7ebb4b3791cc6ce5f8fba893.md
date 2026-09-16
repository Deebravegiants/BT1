### Title
`SimplexPaymaster` prices gas exclusively from Chainlink `latestRoundData()` with no L2 sequencer-uptime check, allowing stale-price gas theft during/after sequencer downtime - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster` is deployed on multiple L2s (Base, Optimism, Arbitrum per `sdk/packages/indexer/src/addresses/chainlink-price-feeds.addresses.ts`) and prices every ERC-4337 gas sponsorship purely from `AggregatorV3Interface.latestRoundData()`, checking only positivity and a `maxOracleAge` staleness bound. It never checks a Chainlink `SequencerUptimeFeed`, so during an L2 sequencer outage and the window immediately after it resumes, the paymaster can charge/refund gas using a price that is stale relative to the true market price, exactly the bug class described in the reference report.

### Finding Description
`_getOraclePrice` in `evm/src/utils/SimplexPaymaster.sol:660-676` only validates: [1](#0-0) 
1. `answer > 0`
2. `block.timestamp - updatedAt <= maxOracleAge`

There is no `SequencerUptimeFeed`/`isSequencerUp` gate anywhere in the contract. `_tokenPrice` (used by both `_fetchDetails` for gas-sponsorship pricing, `getTokenPrice`, `estimateTokenCost`, and by `swapAndDeposit` for fee recycling) is computed directly from these two oracle reads: [2](#0-1) 

Chainlink price updaters cannot submit new rounds to an L2 whose sequencer is down. When the sequencer stalls, `updatedAt` for both `nativeOracle` and each `tokenOracle` freezes at the pre-outage value while `block.timestamp` on L2 also stalls (it only resumes once new blocks are produced). Once the sequencer restarts, `block.timestamp` snaps forward, but the last recorded price can still be well inside `maxOracleAge` — the contract's own comment documents very loose staleness windows ("BSC stablecoins ~27s, Base/Ethereum stablecoins up to 24h" — `evm/src/utils/SimplexPaymaster.sol:146-148`) — while the true off-chain market price (particularly for the native asset, e.g. ETH/BNB, which is far more volatile than the stablecoins) may have already moved substantially. During this window the contract has no mechanism to detect that the sequencer was recently down and that the price is unreliable, unlike the Chainlink-recommended pattern of gating on a `SequencerUptimeFeed` plus a grace period after it comes back up.

This is the same root cause identified in the referenced Aloe report: a protocol relies on a Chainlink price feed on an L2 without accounting for sequencer downtime, so users can transact against a stale price the instant the feed lags reality.

### Impact Explanation
Any unprivileged UserOp sender who reaches `SimplexPaymaster` through `_validatePaymasterUserOp` / `_fetchDetails` (a permissionless ERC-4337 paymaster, per its own header: "Fully onchain, permissionless ERC-4337 v0.8 paymaster") can time a UserOp to land during/right after a sequencer outage:
- If the stale price undercounts the native asset relative to the token (`nativeUsd` too low), the sender pays too little `token` for the actual native gas the paymaster spends, directly draining the paymaster's EntryPoint deposit/treasury reserves — a concrete theft of protocol-controlled funds.
- Conversely, mispricing can also cause `swapAndDeposit` (`evm/src/utils/SimplexPaymaster.sol:454-480`) to execute unfavorable fee-recycling swaps using the same stale `nativeUsd`/`tokenUsd` pair to compute `amountOutMin`, harming the treasury.

Because the paymaster funds gas sponsorship from its own EntryPoint stake/deposit, repeated exploitation during outages is a direct value-extraction vector against protocol-held funds, not merely a user-level loss.

### Likelihood Explanation
L2 sequencer outages are a recurring, observed event on Arbitrum, Optimism, and Base (all deployment targets for this contract). The staleness window is configurable up to `MAX_ORACLE_AGE = 7 days` and the deployed defaults noted in the code comments are already as loose as 24 hours for some stablecoin feeds, so a short-to-medium sequencer outage (well within real-world historical outage durations) will not trip `StaleOraclePrice`, leaving a practically exploitable window. Exploitation requires only submitting an ordinary UserOp through any bundler once the sequencer resumes — no special privilege, governance access, or additional infrastructure.

### Recommendation
Add a Chainlink `SequencerUptimeFeed` check (as documented at https://docs.chain.link/data-feeds/l2-sequencer-feeds) to `_getOraclePrice`/`_tokenPrice`:
- Revert if the sequencer is currently reported down.
- Revert (or reject sponsorship) for a configurable grace period after the sequencer's `startedAt` timestamp indicates it just came back online, so oracle updaters have time to catch up before the paymaster trusts the feed again.

### Proof of Concept
1. Governance registers `SimplexPaymaster` with `nativeOracle` = ETH/USD and a token (e.g. USDC) oracle, with `maxOracleAge` set to a realistic Chainlink heartbeat (e.g., 1 hour for the native feed, as allowed by `MAX_ORACLE_AGE`).
2. The L2 sequencer (e.g., Arbitrum/Base/Optimism) goes down while ETH price is $3000; both oracles' `updatedAt` freeze.
3. ETH price crashes to $2500 off-chain during the outage.
4. Sequencer resumes; `block.timestamp` advances, but `updatedAt` for `nativeOracle` is still within `maxOracleAge` (e.g., outage < 1 hour), so `_getOraclePrice` returns the stale $3000 ETH price — `_getOraclePrice` in `evm/src/utils/SimplexPaymaster.sol:662-676` performs no sequencer-liveness check and accepts it.
5. An attacker immediately submits a UserOp using mode `0x00`/`0x02` paying gas in USDC; `_tokenPrice` (`evm/src/utils/SimplexPaymaster.sol:653-658`) computes `tokenPrice` from the stale $3000 ETH figure instead of the real $2500, so the attacker's actual gas cost (charged in ETH from the paymaster's EntryPoint deposit) is undercompensated by the USDC collected, extracting value from the paymaster on every sponsored operation until the oracle updates.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L653-658)
```text
    function _tokenPrice(TokenConfig memory cfg) internal view returns (uint256) {
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);

        return (nativeUsd * (10 ** cfg.tokenDecimals) * (10_000 + markupBps)) / (tokenUsd * 10_000);
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L662-676)
```text
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
