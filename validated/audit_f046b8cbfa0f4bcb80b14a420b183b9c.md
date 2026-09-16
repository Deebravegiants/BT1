### Title
Missing Chainlink `minAnswer`/`maxAnswer` sanity check in `SimplexPaymaster._getOraclePrice` allows mispriced gas payments during a token flash-crash - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster` prices ERC-20 gas payments for any unprivileged ERC-4337 `UserOperation` sender (a "bandwidth purchaser") by calling `AggregatorV3Interface.latestRoundData()` on both the native/USD and token/USD Chainlink feeds and only checking staleness and a non-positive answer. It never validates the returned `answer` against the underlying Chainlink aggregator's `minAnswer`/`maxAnswer` bounds, so during a flash-crash of a supported gas-payment token the feed can report a price far above the token's real market value, letting an attacker pay for gas with a worthless token at an inflated valuation.

### Finding Description
`_getOraclePrice` is the sole pricing primitive for both the native asset and any registered ERC‑20 payment token: [1](#0-0) 

It only enforces `answer <= 0` reverts and a staleness bound on `updatedAt`; it never compares `answer` to the Chainlink aggregator's configured `minAnswer`/`maxAnswer` circuit-breaker bounds. This mirrors exactly the reported bug class: Chainlink feeds clamp reported values to `[minAnswer, maxAnswer]`, so during a "Black Swan"/flash-crash event where the real price falls below `minAnswer`, the feed keeps returning `minAnswer` — a stale floor that is materially higher than the true collapsed price — while `latestRoundData()` still reports a fresh `updatedAt` and a positive `answer`, passing every check `_getOraclePrice` performs.

`_tokenPrice` consumes this unchecked value directly to compute how many payment tokens are owed per unit of gas: [2](#0-1) 

Because `tokenUsd` sits in the denominator, an inflated `tokenUsd` (the clamped `minAnswer` floor, higher than the token's real crashed value) *reduces* the number of payment tokens the paymaster charges for a given amount of gas. Any address can trigger this pricing path by submitting a `UserOperation` naming the crashed token via `fetchDetails`/`validatePaymasterUserOp`, which is registered as a supported gas token through `RegisterToken` governance and is reachable by every ordinary bundler-submitted operation — no privileged role is required to trigger the mispricing, only to have previously listed the token.

### Impact Explanation
An attacker who acquires the crashed/depegged token at its real (near-zero) market price can use it to pay for real gas sponsorship out of the paymaster's EntryPoint deposit at the stale, inflated Chainlink floor price, draining native-asset value from the paymaster's treasury/deposit for tokens that are actually worthless. This is a concrete theft-of-funds vector against the paymaster's EntryPoint deposit/treasury, matching the "Medium" severity of the original finding (bad pricing leading to funds being drained through undercharging during a flash crash), scaled to this contract's specific role as a gas-payment pricing oracle consumer.

### Likelihood Explanation
Exploitation requires only: (1) the paymaster has a registered token whose Chainlink feed has hit its `minAnswer` floor (a documented, historically-observed Chainlink behavior during flash crashes/depegs), and (2) submitting a normal `UserOperation` using that token — no special privileges, front-running, or governance access needed. The `maxOracleAge` staleness check does not protect against this because the feed continues to update fresh rounds at the clamped floor value.

### Recommendation
In `_getOraclePrice`, additionally query the underlying Chainlink aggregator's `minAnswer()`/`maxAnswer()` (via the aggregator exposed by the proxy, e.g. `aggregator()` on `AggregatorV3Interface` proxies, or by configuring these bounds per feed in `TokenConfig`/`Params`) and revert if `answer` is at or outside those bounds, consistent with the recommended fix in the original Chainlink `minAnswer` audit finding.

### Proof of Concept
1. Governance registers token `T` with Chainlink feed `F` via `RegisterToken` (`SimplexPaymaster.sol` `RequestKind.RegisterToken`).
2. `T`'s real market price collapses (e.g. depeg/flash-crash) to a value below `F`'s configured `minAnswer`. `F.latestRoundData()` keeps returning `minAnswer` with a fresh `updatedAt`.
3. Attacker acquires `T` cheaply on the open market at its true crashed price.
4. Attacker submits a `UserOperation` with `paymasterData` selecting mode 0x00/0x01/0x02 for token `T`; `_tokenPrice`/`_getOraclePrice` (`evm/src/utils/SimplexPaymaster.sol:653-676`) computes the required `T` amount using the stale `minAnswer` floor instead of the real crashed price, charging far fewer real-value tokens than the gas actually costs.
5. The paymaster's EntryPoint deposit pays real gas while receiving near-worthless `T`, repeatable until the deposit or treasury surplus is drained.

### Citations

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
