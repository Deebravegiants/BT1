### Title
`SimplexPaymaster` prices ERC-20 gas fees from Chainlink feeds with no L2 sequencer-uptime check, allowing gas theft/mispricing during sequencer downtime - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster` is a permissionless ERC-4337 paymaster deployed on multiple L2 rollups (Arbitrum, Base, Optimism, Soneium, per `tesseract/messaging/evm/src/registry.rs` `SUPPORTED_L2_CHAIN_IDS_MAINNET` and the paymaster's own BSC/Base test comments) that charges ERC-20 gas fees priced off Chainlink `AggregatorV3Interface` feeds. Its oracle-consumption helper only checks price positivity and feed-update staleness, never whether the underlying L2 sequencer is currently up, unlike Chainlink's documented guidance for L2 deployments.

### Finding Description
`_getOraclePrice` in `evm/src/utils/SimplexPaymaster.sol` reads `latestRoundData()` from a configured token/native Chainlink feed and only validates that the answer is positive and not stale relative to `maxOracleAge`: [1](#0-0) 

This price feed drives `_tokenPrice`, which is used both in the ERC-4337 hot path (`_fetchDetails`, called from `_validatePaymasterUserOp`/`_postOp` on every sponsored UserOp) to compute how much ERC-20 token to charge a user for gas, and in `swapAndDeposit` to compute the minimum acceptable swap output when recycling collected fees: [2](#0-1) [3](#0-2) 

On optimistic-rollup L2s (Arbitrum, Optimism, Base, and other OP-stack/Orbit chains this contract is deployed to per `tesseract/messaging/evm/src/registry.rs`), when the sequencer goes down, L2 timestamps and blocks stop advancing while the underlying Chainlink oracle (typically fed cross-chain or via a keeper that itself depends on chain liveness) can either freeze at a stale-but-not-yet-expired value, or — once the sequencer resumes after an outage — a burst of blocks can be processed with a native/token USD price that has since moved sharply, without any of it being caught by the `maxOracleAge` staleness check, because `block.timestamp` on the L2 during the sequencer gap does not reflect real-world elapsed time and the price feed itself may report an `updatedAt` that appears within bounds. Chainlink explicitly recommends checking a dedicated `SequencerUptimeFeed` and enforcing a grace period after the sequencer comes back online before trusting any price read on these networks; `SimplexPaymaster` has no such check anywhere in its code (`grep` for "sequencer" in `evm/src/**` returns no matches).

### Impact Explanation
Any address able to submit a sponsored UserOp through `SimplexPaymaster` (an intent solver relying on the no-bundler paymaster-sponsored fill path referenced in `sdk/packages/sdk/src/protocols/intents/GasEstimator.ts`, or any ERC-4337 sender) interacts with pricing that is unsafe during/around L2 sequencer downtime:
- Users/solvers can be overcharged or undercharged for gas in the sponsored ERC-20 token if the price used diverges from the true market price during the outage window, directly transferring value between the sender and the paymaster's treasury.
- `swapAndDeposit`'s oracle-derived `amountOutMin` slippage floor becomes unreliable in the same window, allowing execution at a stale/mispriced rate when recycling fees, resulting in a worse-than-expected native output landing in the paymaster (and ultimately treasury) versus what governance intended, or opening a window for value extraction once the sequencer/oracle desyncs and resyncs.

This is a concrete funds-mispricing/theft vector reachable from an unprivileged transaction (a UserOp), consistent with Medium severity per the original oracle-integration report.

### Likelihood Explanation
L2 sequencer outages, while infrequent, are a recurring and well-documented occurrence on Arbitrum/Optimism/Base-class chains, and `SimplexPaymaster` is explicitly deployed to these chains. Any user or solver submitting a UserOp during or immediately after such downtime triggers the vulnerable price path without any special privileges, and the contract offers no reversion or grace-period gate to block pricing during that window, making exploitation solely dependent on sequencer-downtime timing rather than any additional attacker capability.

### Recommendation
Integrate a Chainlink `SequencerUptimeFeed` (per-L2) check into `_getOraclePrice` (or a wrapper called before it): revert if the sequencer is reported down, and revert for a configurable grace period after it comes back up, mirroring the pattern Chainlink documents for L2 price-feed consumers. Apply this consistently to both the `_tokenPrice`/`_fetchDetails` hot path and the `swapAndDeposit` slippage calculation.

### Proof of Concept
1. `SimplexPaymaster` is deployed on an L2 with a Chainlink sequencer-uptime feed (e.g., Arbitrum), registered with a token/USD and native/USD `AggregatorV3Interface` feed, `maxOracleAge` set to the feed's normal heartbeat.
2. The L2 sequencer goes offline. During the outage, no new L2 blocks/timestamps advance normally on-chain, but once transactions resume being processed (either through the resumed sequencer or, on Arbitrum, via the delayed-inbox), `_getOraclePrice` (`evm/src/utils/SimplexPaymaster.sol` lines 662-676) is called with a `block.timestamp` and stale `updatedAt` gap that does not necessarily exceed `maxOracleAge`, since elapsed real-world time and L2-reported time do not correlate during the outage.
3. A solver or user submits a UserOp with `mode 0x00`/`0x02` paymasterData referencing this paymaster while the true off-chain market price of the native asset or token has moved materially versus the frozen/soon-to-update oracle answer.
4. `_fetchDetails` → `_tokenPrice` returns a stale ratio, and `_erc20Cost`/`_prefund` charge the sender using this mispriced ratio, resulting in the sender being over- or under-charged relative to fair value — with no sequencer-status check anywhere in the contract to prevent this (confirmed by absence of "sequencer" references in `evm/src/**`).

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L460-467)
```text

        uint256 balance = IERC20(token).balanceOf(address(this));
        if (amountIn == 0 || amountIn > balance) amountIn = balance;

        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L516-545)
```text
    /// @dev Returns the token to charge and its price relative to native gas.
    ///
    ///      PaymasterERC20 computes `erc20Cost = weiCost * tokenPrice / 1e18`,
    ///      so tokenPrice must be token base units per wei, scaled by 1e18:
    ///        tokenPrice = (nativeUsd * 10^tokenDecimals) / tokenUsd
    ///      e.g. BNB at $600, USDC at $1 with 6 decimals: 0.001 BNB (1e15 wei)
    ///      should cost 0.60 USDC (600000 units), giving tokenPrice = 6e8, which
    ///      is exactly (600e8 * 1e6) / 1e8. Markup is applied on top.
    function _fetchDetails(
        PackedUserOperation calldata userOp,
        bytes32 /* userOpHash */
    )
        internal
        view
        override
        returns (uint256 validationData, IERC20 token, uint256 tokenPrice)
    {
        bytes calldata data = userOp.paymasterData();
        if (data.length < 21) revert InvalidPaymasterData(data.length);

        uint8 mode = uint8(data[0]);
        if (mode != 0x00 && mode != 0x02) revert InvalidMode(mode);

        address tokenAddr = address(bytes20(data[1:21]));

        TokenConfig memory cfg = tokenConfigs[tokenAddr];
        if (address(cfg.tokenOracle) == address(0)) revert TokenNotRegistered(tokenAddr);
        if (!cfg.active) revert TokenNotActive(tokenAddr);

        tokenPrice = _tokenPrice(cfg);
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
