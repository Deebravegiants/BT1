### Title
Missing Chainlink L2 Sequencer Uptime Feed check in SimplexPaymaster's oracle pricing - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster` prices ERC-20 gas payments and treasury swaps using Chainlink `AggregatorV3Interface.latestRoundData()` directly, with only a staleness (`maxOracleAge`) and non-positive-answer check. It never consults an L2 Sequencer Uptime Feed, even though the contract is explicitly documented and deployed on OP-Stack L2s such as Base [1](#0-0) .

### Finding Description
`_getOraclePrice` fetches the Chainlink round data and only validates the answer's sign and its age relative to `block.timestamp`: [2](#0-1) 

This is the same pattern flagged in the external report: on L2s, `block.timestamp` and transaction inclusion can continue to advance from queued/forced transactions even while the sequencer (and thus the price-feed relayer that updates on the L2) is down or has just come back online. Chainlink's documented mitigation for this exact scenario is to check a chain's `SequencerUptimeFeed` and enforce a grace period after it reports the sequencer is back up, which is what `_getOraclePrice` omits entirely — it has no sequencer feed reference at all. Both `_tokenPrice` (used for every ERC-4337 `_fetchDetails`/`_prefund` gas payment) and `swapAndDeposit` (treasury fee-recycling swap) rely on this unguarded price: [3](#0-2) [4](#0-3) 

`_fetchDetails` is invoked for every UserOperation an unprivileged sender submits to pay gas with a registered ERC-20 token, so this pricing path is reachable by any ordinary paymaster user, not just governance/treasury: [5](#0-4) 

### Impact Explanation
If the Base (or any OP-Stack) sequencer is down or has just resumed, `updatedAt` on the Chainlink feed can remain within `maxOracleAge` while the reported price is stale/unreliable relative to true market conditions, or a forced/queued transaction can execute against out-of-date pricing before the feed catches up. Because `_tokenPrice`/`_getOraclePrice` is the sole gate for how much ERC-20 tokens are charged per unit of gas in `_fetchDetails`, an attacker (or simply an opportunistic user) could submit UserOperations that pay/settle against a mispriced rate during this window, extracting value from the paymaster's treasury (underpaying for sponsored gas) or from `swapAndDeposit`'s slippage-bounded swap being executed against a bad reference price. This is a concrete funds-loss vector for the treasury/solver capital that backs the paymaster.

### Likelihood Explanation
The paymaster is explicitly designed for and documented as deployable on OP-Stack L2s like Base, where sequencer downtime/restart windows are an established, documented occurrence for which Chainlink itself recommends the uptime-feed mitigation. Any user submitting a UserOperation through the paymaster reaches this code path — no privileged role is required — so likelihood is tied only to sequencer availability events on the deployed L2, which are not rare or exotic.

### Recommendation
Add an L2 Sequencer Uptime Feed check (per-chain configurable, similar to `nativeOracle`) in `_getOraclePrice`, reverting or holding a grace period whenever the sequencer feed reports downtime or was recently restored, mirroring Chainlink's documented `SequencerUptimeFeed` pattern, before trusting `latestRoundData()` results from `nativeOracle`/`tokenOracle`.

### Proof of Concept
1. Deploy `SimplexPaymaster` on Base (an OP-Stack L2), registering a token with its Chainlink `tokenOracle` and configuring `nativeOracle`, per `_registerToken`/`_updateParams`.
2. Simulate a Base sequencer outage/restart window in which `latestRoundData()`'s `updatedAt` stays inside `maxOracleAge` (e.g., a heartbeat that hasn't yet expired) but the reported `answer` no longer reflects the true market price (as Chainlink's own L2 guidance describes as a known risk during sequencer downtime/restart).
3. Submit a UserOperation through the paymaster's `_fetchDetails`/`_prefund` path paying with the mispriced token; `_getOraclePrice` accepts the stale-but-not-yet-expired price with no sequencer check [6](#0-5) , letting the operation settle at an incorrect exchange rate and drain value from the paymaster's treasury-backed gas subsidy.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L146-148)
```text
        /// @notice Maximum oracle staleness. Chainlink heartbeats vary per chain
        ///         (BSC stablecoins ~27s, Base/Ethereum stablecoins up to 24h).
        uint256 maxOracleAge;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L464-467)
```text
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L524-545)
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
