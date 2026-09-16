### Title
Premature downscaling of Chainlink oracle prices to 8 decimals in `SimplexPaymaster` causes systematic undercharging of ERC-20 gas fees - ([File: evm/src/utils/SimplexPaymaster.sol])

### Summary
`SimplexPaymaster._getOraclePrice()` truncates the raw Chainlink `answer` down to 8 decimals before it is used in `_tokenPrice()` to compute the ERC-20 amount a UserOp sender is charged for gas. For any oracle with `oracleDecimals > 8` (e.g. an 18-decimal token/USD feed, exercised by the repo's own `testTokenPriceNormalizesOracleDecimals` test), the intermediate integer division discards up to `10**(oracleDecimals-8) - 1` units of precision from the price *before* it is combined with the native price and token decimals, exactly the bug class described in the reference report (Chainlink price downscaled prematurely rather than normalized at point of use).

### Finding Description
`_getOraclePrice` is: [1](#0-0) 

and it feeds directly into `_tokenPrice`, the function that determines how many ERC-20 base units of the fee token every UserOp sender is charged for gas: [2](#0-1) 

Both `nativeOracle` and every registered token's `tokenOracle` are normalized through `_getOraclePrice`, and its 8-decimal target is fixed regardless of the feed's native precision: [3](#0-2) [4](#0-3) 

For any feed registered with `decimals() > 8` (the contract explicitly supports this — see the `> 8` branch and the paymaster's own test using an 18-decimal oracle), the division `answer / 10**(oracleDecimals-8)` truncates toward zero, i.e. always rounds the price *down*. This is the same root cause as the reference finding: the raw price is downscaled and stored/used at reduced precision instead of keeping full precision and normalizing only at the point of consumption (here, inside `_tokenPrice`/`_erc20Cost`).

Because Solidity integer division always rounds down, this truncation is directionally biased, not random: `tokenUsd` (denominator in `_tokenPrice`) is rounded down, which increases the computed `tokenPrice` (nativeUsd * tokenDecimals * markup / tokenUsd), while `nativeUsd` (numerator) rounding down decreases it. The net effect on the charge depends on which oracle has the higher-precision feed, but in either case, the per-operation charge deviates from the true market price by a rounding error of up to one part in `10**(oracleDecimals-8)`, applied every single UserOp validated by `_fetchDetails`/`_prefund`, which are on the unprivileged, permissionless UserOp-submission path (any account can submit a paymasterData-bearing UserOp; no governance/relayer gating applies to `_validatePaymasterUserOp`, `_fetchDetails`, `_prefund`, or `estimateTokenCost`).

### Impact Explanation
The paymaster charges gas in registered ERC-20 tokens via `tokenPrice` in `_fetchDetails` (used by `_erc20Cost` in `_prefund`), so an under-priced `tokenUsd` (from truncating a >8-decimal token/USD feed) inflates `tokenPrice`, causing users to be systematically overcharged for gas on every UserOp; conversely an under-priced `nativeUsd` deflates `tokenPrice`, causing systematic undercharging (a drain on the paymaster's treasury/markup surplus over the life of the contract, and by extension on the EntryPoint deposit funded by `swapAndDeposit`, which also uses `_getOraclePrice`). Given `swapAndDeposit` and `_tokenPrice` share the same truncated oracle values, the deployer could register an 18-decimal Chainlink feed (fully within the documented, supported oracle-decimals range) and every UserOp/gas-recycling swap thereafter compounds this rounding bias — a repeatable value leak reachable by unprivileged UserOp senders, not just governance-configured behavior.

### Likelihood Explanation
Likelihood is contingent on a token/native oracle actually using more than 8 decimals (Chainlink's most common convention is 8 decimals for USD pairs, but 18-decimal feeds exist and are explicitly supported/tested in this codebase — `testTokenPriceNormalizesOracleDecimals`). Since `RegisterToken`/`UpdateParams` governance requests can register any Chainlink-compatible aggregator, and nothing in `_registerToken`/`_setParams` rejects high-decimal feeds, the precision loss is a latent, systemic issue for any such deployment, silently biasing every gas charge rather than an isolated edge case.

### Recommendation
Do not fix the price to 8 decimals as an intermediate representation. Instead, keep each oracle's native `answer` and `oracleDecimals` and normalize decimals only inside `_tokenPrice` (and `swapAndDeposit`'s cost estimate) at the point where `nativeUsd` and `tokenUsd` are combined, using a single common target precision applied multiplicatively (scale the lower-precision side up) rather than dividing the higher-precision side down. This mirrors the reference recommendation of carrying full precision and normalizing decimals only at the point of use in `getDollarInCollateral()`-equivalent computations.

### Proof of Concept
1. Deploy `SimplexPaymaster` with `nativeOracle` at 8 decimals (e.g., `600e8` = $600/native) and register a token with an 18-decimal `tokenOracle` reporting `999999999999999999` ($0.999999999999999999/token) instead of a clean `1e18`.
2. `_getOraclePrice` computes `999999999999999999 / 10**10 = 99999999` (8-decimal truncation), losing the fractional cent-level precision below 8 decimals — the raw price was ~$0.999999999999999999 but is now treated as $0.99999999.
3. `_tokenPrice` uses this truncated `tokenUsd` as the denominator, inflating `tokenPrice` versus the true value, so `_erc20Cost` (called from `_prefund`) charges every UserOp sender using that token slightly more ERC-20 units than the true market rate implies — a bias that compounds across all UserOps validated while that feed is registered.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L196-197)
```text
    AggregatorV3Interface public nativeOracle;
    uint8 public nativeOracleDecimals;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L392-397)
```text
        tokenConfigs[token] = TokenConfig({
            tokenOracle: oracle,
            tokenOracleDecimals: oracle.decimals(),
            tokenDecimals: IERC20Metadata(token).decimals(),
            active: true
        });
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
