### Title
Missing Chainlink L2 sequencer-uptime check in `SimplexPaymaster` oracle pricing - ([File: evm/src/utils/SimplexPaymaster.sol])

### Summary
`SimplexPaymaster` prices ERC-20 gas payments using two Chainlink `AggregatorV3Interface.latestRoundData()` feeds (native/USD and token/USD) and only guards against staleness via a simple `block.timestamp - updatedAt > maxOracleAge` check. It never checks an L2 sequencer-uptime feed, even though the contract is explicitly designed to be deployed across many chains, including L2s (comments reference "BSC stablecoins", "Base/Ethereum stablecoins", and the paymaster is a general-purpose deployable utility). This mirrors the Iron Bank finding: Chainlink price feeds on L2s like Arbitrum/Optimism/Base can report data that passes a naive `updatedAt`-based staleness check while being stale relative to real market conditions during/around a sequencer outage.

### Finding Description
`_getOraclePrice` fetches Chainlink data and only validates non-negativity and heartbeat-based staleness: [1](#0-0) 

This function is called by `_tokenPrice`, which is invoked from `getTokenPrice`, `estimateTokenCost`, and — critically — the paymaster validation path that every unprivileged ERC-4337 `UserOperation` sender reaches via `paymasterData` (`fetchDetails` → `_tokenPrice` → `_getOraclePrice`). Any account abstraction user submitting a `UserOperation` that uses this paymaster for gas sponsorship in ERC-20 (mode 0x00/0x02) causes `_getOraclePrice` to be evaluated on both the native and the token oracle.

The deployment script confirms the paymaster is meant for cross-chain reuse with a configurable `maxOracleAge`: [2](#0-1) 

No code path anywhere in `SimplexPaymaster.sol` references a sequencer-uptime feed (e.g., Chainlink's `L2SequencerUptimeFeed`), nor is there any check that the sequencer has been up for a minimum grace period before trusting `latestRoundData()`. On Arbitrum/Optimism/Base, when the sequencer is degraded or has just resumed after downtime, Chainlink price feeds can report an `updatedAt` timestamp that still satisfies `block.timestamp - updatedAt <= maxOracleAge` while the price is stale relative to the real market — exactly the scenario the sequencer-uptime check exists to catch, per Chainlink's own L2 documentation cited in the source report.

### Impact Explanation
If an attacker (any unprivileged account abstraction sender, since `SimplexPaymaster` is "fully onchain, permissionless") submits `UserOperation`s during or immediately after an L2 sequencer outage, the paymaster may price ERC-20-for-gas swaps using a favorable stale rate. Because the paymaster custodies pooled EntryPoint deposits and accepts ERC-20 in exchange for sponsoring gas (per the contract's own documentation, it accumulates markup surplus and refunds unused gas), a mispriced native/token rate directly transfers value out of the paymaster's treasury/EntryPoint deposit to attacker-controlled accounts — a concrete theft-of-funds vector, satisfying the "Medium" bar (comparable to the original Iron Bank finding).

### Likelihood Explanation
Likelihood is moderate: it requires a live L2 sequencer outage/restart window on whichever chain the paymaster is deployed, combined with either forced-inclusion transaction submission (available on some L2s during sequencer downtime) or exploitation right as the sequencer resumes and before Chainlink price feeds catch up. This is the same precondition class flagged as Medium severity in the source Iron Bank report, and the contract's own documentation and deploy tooling show it is intended for multi-chain (including L2) deployment, so the risk is not merely theoretical for a single-chain-only contract.

### Recommendation
Integrate Chainlink's `L2SequencerUptimeFeed` (per-chain, configurable via governance like the existing `Params`/`TokenConfig`) into `_getOraclePrice`: check `latestRoundData()` on the uptime feed, require `answer == 0` (up) and enforce a grace period (e.g. Chainlink's recommended `GRACE_PERIOD_TIME`) since `startedAt` before trusting any price read, reverting otherwise. This should gate both the native oracle and token oracle reads used in `_tokenPrice`.

### Proof of Concept
1. Deploy `SimplexPaymaster` on an L2 (e.g., Arbitrum) with `nativeOracle`/`tokenOracle` set to real Chainlink feeds, per `DeploySimplexPaymaster.s.sol`.
2. Simulate/await an L2 sequencer outage window; Chainlink feed continues to report the last round with `updatedAt` inside `maxOracleAge` (e.g., a 90000s window as in the deploy defaults) even though the true market price has since moved unfavorably to the paymaster's treasury.
3. Submit (or have force-included) a `UserOperation` with `paymasterData` mode `0x00`/`0x02` referencing the stale-favorable rate; `fetchDetails` → `_tokenPrice` → `_getOraclePrice` (evm/src/utils/SimplexPaymaster.sol:662-676) accepts the stale price because it only checks `answer > 0` and `block.timestamp - updatedAt <= maxOracleAge`, with no sequencer-uptime gate.
4. The attacker's ERC-20 payment is priced against the stale rate, extracting value from the paymaster's EntryPoint deposit/treasury beyond what the true market rate would allow.

### Citations

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

**File:** evm/script/DeploySimplexPaymaster.s.sol (L14-21)
```text
    function deploy() internal override {
        address nativeOracleAddr = config.get("NATIVE_ORACLE").toAddress();
        uint256 markupBps = vm.envOr("MARKUP_BPS", uint256(200)); // default 2%
        address treasury = vm.envOr("TREASURY", admin); // default to deployer
        // Stablecoin feeds on Ethereum and Base run a 24h heartbeat; a buffer over
        // 24h avoids transient StaleOraclePrice reverts on late pushes.
        uint256 maxOracleAge = vm.envOr("MAX_ORACLE_AGE", uint256(90_000));
        uint256 swapSlippageBps = vm.envOr("SWAP_SLIPPAGE_BPS", uint256(200)); // default 2%
```
