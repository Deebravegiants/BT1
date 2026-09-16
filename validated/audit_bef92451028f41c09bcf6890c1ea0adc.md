This confirms `SimplexPaymaster` is deployed on Base and Ethereum (line 18-19 comment: "Stablecoin feeds on Ethereum and Base run a 24h heartbeat"), meaning it operates on OP Stack chains (Base) that do have a Chainlink Sequencer Uptime Feed available and relevant. `_getOraclePrice` in `SimplexPaymaster.sol` only checks `answer <= 0` and `block.timestamp - updatedAt > maxOracleAge`, without verifying the L2 sequencer's uptime status, matching the exact bug class of the reported issue.

### Title
Missing L2 sequencer uptime check in SimplexPaymaster's Chainlink price consumption on OP Stack chains (Base) - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster` consumes Chainlink `AggregatorV3Interface` price feeds (`nativeOracle` and per-token oracles) on Base, an OP Stack L2 with a centralized Sequencer. Its `_getOraclePrice` helper only validates that the answer is positive and not older than `maxOracleAge`, but never checks Chainlink's L2 Sequencer Uptime Feed as Chainlink's own documentation recommends for all Optimistic L2 deployments.

### Finding Description
`_getOraclePrice` is the sole gate on Chainlink data used throughout the contract's pricing path: [1](#0-0) 

It is called from `_tokenPrice` (used by `getTokenPrice`, `estimateTokenCost`, and the UserOp `fetchDetails`/prefund pricing path) and directly from `swapAndDeposit`: [2](#0-1) [3](#0-2) 

The deployment script's own comment establishes that this contract is deployed on Base (an OP Stack chain with a Sequencer and an available `SequencerUptimeFeed`): [4](#0-3) 

If Base's sequencer goes down, the last relayed Chainlink `updatedAt` timestamp freezes at the moment of the outage. Because L2 `block.timestamp` also stops advancing while the sequencer is halted (no new L2 blocks are produced), the elapsed-time check `block.timestamp - updatedAt > maxOracleAge` can be trivially satisfied even though the price is stale in wall-clock/L1 time — the on-chain age simply never grows while the sequencer is down. When the sequencer resumes and a user (or the batch of queued transactions submitted via the L1 force-inclusion path) is finally processed, a large real-world price move (e.g. a native asset crash or spike) can occur between the last valid update and the resumption of service, and the contract will treat the frozen, now-invalid price as fresh because the on-chain clock never accumulated the elapsed downtime.

This directly mirrors the reported bug class: reliance on Chainlink feeds on an Optimistic L2 without consulting `AggregatorV3Interface(sequencerUptimeFeed).latestRoundData()` and enforcing the recommended `GRACE_PERIOD_TIME` after the sequencer is reported "up" again.

### Impact Explanation
Any unprivileged UserOp submitter interacting with `SimplexPaymaster` (an `unprivileged message dispatcher`-analogous entry point: `fetchDetails`/`postOp` gas-sponsorship pricing) can have their ERC-20 gas payment priced using a stale-but-"fresh-looking" Chainlink answer during/immediately after a sequencer outage. Because pricing under- or over-charges tokens relative to the true native-asset cost, this can result in:
- Underpricing: users pay far less in ERC-20 tokens than the native gas actually costs, directly draining the paymaster's EntryPoint deposit/treasury surplus (fund loss for the protocol).
- Overpricing: users are overcharged, a fund-loss/griefing vector against callers.

`swapAndDeposit` similarly derives `amountOutMin` from the same unchecked path, allowing execution at a stale exchange rate during fee-recycling swaps, which can be sandwiched/arbitraged against the treasury.

### Likelihood Explanation
Requires an actual Base/OP-Stack sequencer downtime event, which is infrequent but has occurred historically for OP Stack chains (documented multi-hour Sequencer outages have happened on Base/Optimism). Given the paymaster is designed to actively operate on Base per its own deployment configuration, and no privileged action is needed to exploit the mispricing window (any UserOp sender or the treasury-gated `swapAndDeposit` caller during that window benefits), likelihood is realistic though outage-dependent — consistent with a Medium severity classification, matching the original report's rating.

### Recommendation
Add a Chainlink `SequencerUptimeFeed` check (per Chainlink's documented pattern) inside `_getOraclePrice`, or as a pre-check in `_tokenPrice`/`swapAndDeposit`: read `latestRoundData()` from the sequencer uptime feed, revert if `answer == 1` (sequencer down), and enforce a grace period (e.g. `GRACE_PERIOD_TIME`, commonly 3600s) after `startedAt` before trusting price data again. Make the sequencer feed address and grace period governance-configurable parameters alongside `maxOracleAge`, mirroring `_setParams`'s existing validation pattern at: [5](#0-4) 

### Proof of Concept
1. Deploy `SimplexPaymaster` on Base per `DeploySimplexPaymaster.s.sol`.
2. Simulate Base sequencer downtime (Chainlink price feed `updatedAt` freezes at time `T0`; L2 `block.timestamp` also stops advancing since no blocks are produced).
3. Off-chain, native asset (e.g., ETH) price moves significantly (e.g., -20%) during the outage.
4. Sequencer resumes; the first processed UserOps still see `block.timestamp - updatedAt` well within `maxOracleAge` (since both clocks were frozen together), so `_getOraclePrice` in `evm/src/utils/SimplexPaymaster.sol:662-676` returns the stale pre-outage price.
5. A UserOp's ERC-20 payment in `_tokenPrice`/`estimateTokenCost` is computed off this stale price, allowing the user to underpay for gas relative to the true post-outage native cost, draining paymaster funds; repeated for many UserOps immediately after resumption compounds the loss.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L357-383)
```text
    /// @dev Validates and applies pricing/treasury parameters, re-caching the
    ///      native oracle decimals.
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
