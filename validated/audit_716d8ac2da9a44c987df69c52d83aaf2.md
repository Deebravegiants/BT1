Based on the analog found, this is a valid analog to the reported bug class.

### Title
Missing Chainlink circuit-breaker bounds check in `SimplexPaymaster._getOraclePrice()` allows mispriced gas sponsorship - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster` prices every ERC-20 gas payment against two Chainlink `AggregatorV3Interface` feeds (`nativeOracle` and each token's `tokenOracle`) through `_getOraclePrice()`. That function only rejects a non-positive answer and a stale `updatedAt`; it never checks the returned `answer` against the aggregator's configured `minAnswer`/`maxAnswer` circuit-breaker bounds. This is the same root cause as the referenced report: when the underlying asset price moves outside the aggregator's band (e.g., a stablecoin depeg or a flash crash), Chainlink's proxy continues to report the clamped `minAnswer`/`maxAnswer` instead of the true price, and the consuming contract has no way to detect this and treats the clamped value as valid, fresh data.

### Finding Description
`_getOraclePrice()` is the sole gate on oracle data used for every ERC-20 gas payment in the paymaster: [1](#0-0) 

The only validations performed are `answer <= 0` and staleness (`block.timestamp - updatedAt > maxOracleAge`). There is no minimum/maximum sanity bound comparable to the Chainlink aggregator's own `minAnswer`/`maxAnswer` circuit breaker. Both the native/USD price and every registered token/USD price computed here feed directly into `_tokenPrice()`: [2](#0-1) 

`_tokenPrice()` is used both for quoting gas cost in `estimateTokenCost()`/the actual `PaymasterERC20` cost calculation that determines how many ERC-20 tokens are pulled from the user during `_postOp`, and for sizing `swapAndDeposit()`'s expected output: [3](#0-2) 

If a registered token (e.g. a stablecoin accepted for gas payment) depegs downward past its Chainlink feed's `minAnswer`, the feed will keep returning `minAnswer` — a price higher than the token's real market value — while still passing the paymaster's freshness and positivity checks. Since `_tokenPrice()` computes `nativeUsd / tokenUsd`, an inflated `tokenUsd` produces an underestimated token-per-wei-of-gas price, so `_erc20Cost` charges users fewer of the (now near-worthless) depegged tokens than the sponsored gas is actually worth. The paymaster sponsors full-value native gas while accepting devalued tokens priced at the stale clamped rate — a direct, permanent loss of paymaster/treasury funds. This is reachable by any unprivileged UserOperation sender who selects a registered depegging token in `paymasterData` — no special privilege is required, only that governance has previously registered that token/feed pair (a normal, expected configuration state, not an admin compromise).

### Impact Explanation
This causes concrete loss of funds: the paymaster's treasury/deposit is drained sponsoring gas in native currency while receiving ERC-20 tokens priced above their real (crashed) value, exactly mirroring the referenced report's mechanism where a Chainlink circuit-breaker-clamped answer causes an oracle consumer to mint/accept value based on a stale extreme price instead of the real one. Because the paymaster is a shared, unprivileged entry point (any UserOperation using PERMIT or PERMIT2 mode can select the depegged token), the loss compounds across every transaction submitted while the feed is clamped, until governance reacts by deactivating the token via `DeactivateToken`.

### Likelihood Explanation
Requires a registered token to actually depeg/crash past its feed's aggregator bounds — a real, observed market event class for stablecoins and low-cap gas-payment tokens, not an artificial or admin-triggered condition. No governance or admin compromise is needed; any user submitting an ordinary UserOperation with the depegged token in `paymasterData` triggers mispriced sponsorship automatically, and the exploit is available to every unprivileged submitter for as long as the clamp persists and no one has deactivated the token yet.

### Recommendation
In `_getOraclePrice()`, fetch (or configure) each aggregator's `minAnswer`/`maxAnswer` circuit-breaker bounds (e.g., via `IChronicle`/`AccessControlledOffchainAggregator.minAnswer()/maxAnswer()`, or store admin-configured bounds per token/native oracle) and revert if `answer <= minAnswer || answer >= maxAnswer`, in addition to the existing staleness and positivity checks:

```solidity
function _getOraclePrice(AggregatorV3Interface oracle, uint8 oracleDecimals, int256 minAnswer, int256 maxAnswer)
    internal view returns (uint256)
{
    (, int256 answer,, uint256 updatedAt,) = oracle.latestRoundData();
    if (answer <= minAnswer || answer >= maxAnswer) revert InvalidOraclePrice(address(oracle), answer);
    ...
}
```
This prevents the paymaster from trusting a clamped circuit-breaker answer as a legitimate market price.

### Proof of Concept
1. Governance registers stablecoin `T` for gas payment via `RegisterToken`, with Chainlink feed `F` whose aggregator has `minAnswer = 0.98e8` (8 decimals) as its lower circuit-breaker bound.
2. `T` depegs to $0.10 due to a real-world exploit/run, but `F.latestRoundData()` continues returning `answer = 0.98e8` (clamped) with a fresh `updatedAt`.
3. `_getOraclePrice()` passes both checks (`answer > 0`, not stale) and returns `98_000_000` (normalized), even though the true price is `10_000_000`.
4. Any user submits a UserOperation with `paymasterData` mode `0x00`/`0x02` referencing `T`; `_tokenPrice()` computes cost using the inflated `tokenUsd = 0.98`, charging roughly 1/10th of the tokens actually needed to cover the sponsored gas at `T`'s real value.
5. The paymaster sponsors the user's gas in full while receiving `T` tokens worth a fraction of the gas cost — repeated across every UserOperation using `T`, this drains the paymaster's EntryPoint deposit/treasury.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L463-467)
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
