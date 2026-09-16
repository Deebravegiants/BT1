### Title
Chainlink oracle price feeds used by `SimplexPaymaster` on Arbitrum/Base/Optimism are not checked against an L2 sequencer-uptime feed - ([File: evm/src/utils/SimplexPaymaster.sol])

### Summary
`SimplexPaymaster._getOraclePrice` calls `AggregatorV3Interface.latestRoundData()` and only validates that the answer is positive and not stale by `maxOracleAge`. It never checks Chainlink's L2 sequencer uptime feed, even though this paymaster is deployed on Arbitrum, Base and other OP-stack/Arbitrum L2 chains.

### Finding Description
`_getOraclePrice` is the sole gate on Chainlink data used for pricing: [1](#0-0) 

It is called from `_tokenPrice` (used by `getTokenPrice`/`estimateTokenCost` and, per the contract's design, by the ERC-4337 validation/postOp cost path that actually deducts a solver's stablecoin balance) and from `swapAndDeposit`'s minimum-output computation: [2](#0-1) [3](#0-2) 

Neither of these call sites, nor `_getOraclePrice` itself, references an `L2SequencerUptimeFeed` or performs a `startedAt`/grace-period check. This paymaster is confirmed to be deployed on Arbitrum (chain 42161) and other L2s: [4](#0-3) 

and the deploy tooling explicitly targets Arbitrum/Base/Optimism among its supported chains: [5](#0-4) 

On these L2s, when the sequencer goes down and later comes back online, Chainlink price feeds can report values that look "fresh" (recent `updatedAt`) immediately after sequencer restart while the true market price may have diverged during the outage, or a malicious/compromised sequencer operator could submit stale-but-passing price reads during the outage window. Chainlink explicitly recommends gating all L2 price consumption on the `SequencerUptimeFeed`'s `answer`/`startedAt` grace period for this reason. `SimplexPaymaster` has no such gate.

### Impact Explanation
`_getOraclePrice`'s result directly drives `_tokenPrice`, which prices the stablecoin amount charged to a solver/user's account for sponsoring their ERC-4337 UserOp gas, and drives the minimum-output guard in `swapAndDeposit`, which converts accrued paymaster stablecoin surplus to native currency. Both paths move real value: an unprivileged UserOp sender (an intent solver relying on Simplex sponsorship) interacts with pricing that is not sequencer-aware, and a treasury-triggered `swapAndDeposit` could execute against a distorted price during/after an L2 sequencer outage. This can result in solvers being under/overcharged for gas relative to the true price (economic loss to the paymaster treasury or to solvers) during a documented, reproducible Chainlink L2 failure mode. This is a Medium-severity issue consistent with the original Iron Bank finding, reachable without any privileged role — any solver submitting a sponsored UserOp during/after a sequencer incident on Arbitrum/Base triggers the affected pricing path.

### Likelihood Explanation
L2 sequencer downtime incidents have occurred historically on Arbitrum and Optimism-stack chains, and the SimplexPaymaster is actively deployed there per the SDK chain configuration and deploy scripts. Any solver's routine sponsored UserOp submission exercises `_tokenPrice`/`_getOraclePrice` with no additional privilege required, so the window is limited only to sequencer-outage/restart periods but requires no attacker action beyond normal transaction submission during that window.

### Recommendation
Add an L2 sequencer-uptime feed check to `_getOraclePrice` (or a wrapper called before it) on all L2 deployments (Arbitrum, Base, Optimism, Soneium, Unichain): read the sequencer feed's `latestRoundData()`, revert if `answer == 1` (sequencer down), and enforce a grace period after `startedAt` (e.g. Chainlink's recommended pattern) before trusting any price feed read on that chain. Since the same `SimplexPaymaster` implementation is shared across L1 and L2 deployments, make this configurable per-deployment (e.g. an optional `sequencerUptimeFeed` address in `Params`, skipped when zero for L1 chains like Ethereum/BSC/Polygon/Gnosis).

### Proof of Concept
1. `SimplexPaymaster` is deployed on Arbitrum with `nativeOracle`/`tokenOracle` set to Chainlink feeds (per `evm/script/DeploySimplexPaymaster.s.sol` and the live Arbitrum address in `chain.ts`).
2. Arbitrum's sequencer experiences an outage; Chainlink price feeds on L2 either stall or, upon sequencer restoration, immediately report a new round with a fresh `updatedAt` that passes `_getOraclePrice`'s staleness check (`block.timestamp - updatedAt <= maxOracleAge`), even though the price could not have been arbitraged/settled correctly during the outage.
3. A solver submits a sponsored UserOp during this window; `_tokenPrice` → `_getOraclePrice` accepts the reported price with no sequencer-liveness verification, mispricing the stablecoin amount charged versus the true gas cost.
4. No revert occurs because `_getOraclePrice` only checks `answer <= 0` and staleness — confirmed at [6](#0-5) , with no `Sequencer`/`sequencer` reference anywhere in `evm/src/**` (confirmed via repository-wide search).

### Citations

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

**File:** sdk/packages/sdk/src/configs/chain.ts (L538-538)
```typescript
			SimplexPaymaster: "0x7281Bccb4f0BCE44F3B8542d1fC5e51c2F5fC08C",
```

**File:** evm/script/deploy.sh (L65-69)
```shellscript
    echo "  Testnets: sepolia, optimism-sepolia, arbitrum-sepolia, base-sepolia,"
    echo "            polygon-amoy, bsc-testnet, gnosis-chiado, polkadot-testnet, pharos-testnet"
    echo ""
    echo "  Mainnets: ethereum, optimism, arbitrum, base, bsc, gnosis,"
    echo "            soneium, polygon, unichain, inkchain, sei"
```
