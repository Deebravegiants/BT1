## Title
Missing L2 sequencer-uptime check in `SimplexPaymaster`'s Chainlink oracle staleness validation allows stale-price gas-fee underpayment - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster` is a permissionless ERC-4337 paymaster that prices ERC-20 gas payments using two Chainlink `AggregatorV3Interface` feeds (native/USD and token/USD) via `_getOraclePrice()`. The only freshness check performed is `block.timestamp - updatedAt > maxOracleAge`, exactly the pattern flagged in the external report for `Kept.sol`'s `_etherPrice()`. There is no check of an L2 sequencer-uptime feed, even though the contract's supported deployment targets (per `sdk/packages/indexer/src/addresses/chainlink-price-feeds.addresses.ts`) include Arbitrum (`EVM-42161`), Optimism (`EVM-10`) and Base (`EVM-8453`), all L2s for which Chainlink explicitly recommends checking sequencer status before trusting `latestRoundData()`.

### Finding Description
`_getOraclePrice()` fetches `latestRoundData()` and only rejects non-positive answers or updates older than `maxOracleAge` (governance-configurable up to `MAX_ORACLE_AGE = 7 days`): [1](#0-0) 

This price feeds directly into `_tokenPrice()`, which is called from `_fetchDetails()` on every paymaster-sponsored `UserOperation` — an unprivileged, permissionless entry point reachable by any bundler/solver submitting a UserOp through this "bandwidth purchaser" gas-payment flow: [2](#0-1) [3](#0-2) 

On Arbitrum (an OP-stack/Orbit style rollup with a documented sequencer), when the sequencer goes down and later resumes, Chainlink price feed updates lag behind real market conditions during and immediately after the outage window. Since `updatedAt` staleness is the only defense, a price that is technically "not stale" (within `maxOracleAge`, which can be configured up to 7 days per `MAX_ORACLE_AGE`) can still reflect stale market conditions relative to the real-time price once the sequencer resumes and transactions can flow again. Chainlink's documented mitigation — checking a dedicated L2 sequencer uptime feed and enforcing a grace period after it comes back online — is absent here, exactly mirroring the missing check identified in the source report for `Kept.sol`.

### Impact Explanation
`_tokenPrice()` computes `tokenPrice = (nativeUsd * 10^tokenDecimals * (10000+markupBps)) / (tokenUsd * 10000)`, which directly determines how much ERC-20 token an op sender is charged for a given amount of gas via `_erc20Cost`. If the price is stale-but-fresh-looking due to sequencer downtime, an attacker can time a UserOp submission (right as the sequencer resumes) to be charged based on a favorable, outdated exchange rate, extracting value from the paymaster's treasury/deposit (paying less in the ERC-20 token than the real-time gas cost, or conversely draining native funds from the EntryPoint deposit relative to token collected) — a concrete theft-of-funds vector against the paymaster's stake. This is a Medium severity oracle-staleness issue consistent with the class of bug in the external report.

### Likelihood Explanation
Exploitability depends on an L2 sequencer downtime-and-recovery event, which is an infrequent but real operational occurrence on Arbitrum/Optimism/Base (all supported deployment targets per the Chainlink feed address registry). Any permissionless submitter of a UserOp (bundler, relayer, or the party paying gas) can trigger the vulnerable code path with no special privileges, so likelihood is bounded only by the occurrence of a sequencer outage/recovery window, not by any access-control barrier.

### Recommendation
Add an L2 sequencer uptime feed check (Chainlink's `SequencerUptimeFeed`) to `_getOraclePrice()` for deployments on sequencer-based L2s (Arbitrum, Optimism, Base), reverting if the sequencer has been down or is within a configurable grace period after restart, mirroring Chainlink's documented `answeredInRound`/uptime-feed pattern.

### Proof of Concept
1. Deploy `SimplexPaymaster` on Arbitrum with a native/USD and token/USD Chainlink feed, `maxOracleAge` set to a permissive value (e.g. hours).
2. Simulate the Arbitrum sequencer going offline for a period during which the real market price of the native asset or the token moves significantly, while the Chainlink feed's `updatedAt` stops advancing (per Chainlink L2 outage behavior).
3. As soon as the sequencer resumes and transactions can be processed again, submit a `UserOperation` through `SimplexPaymaster` using mode `0x00`/`0x02` paymasterData while the feed is still within `maxOracleAge` but reflects the pre-outage (stale) price.
4. `_fetchDetails` → `_tokenPrice` → `_getOraclePrice` returns the stale price without any staleness revert (since `updatedAt` age check alone passes), so the op sender is charged an incorrect (attacker-favorable) `tokenPrice`, extracting value from the paymaster relative to the true post-outage market price.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L524-547)
```text
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
        token = IERC20(tokenAddr);
        validationData = 0; // no time-range restriction
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
