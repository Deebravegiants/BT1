### Title
Stale Chainlink prices in `SimplexPaymaster` let solvers underpay for sponsored gas - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster._getOraclePrice` prices gas exactly the way the referenced Notional bug describes: it trusts `latestRoundData()` as if it were the *current* price, only bounding staleness by a configurable ceiling (up to `MAX_ORACLE_AGE = 7 days`, deployed default ~25h) rather than requiring a fresh update. Any unprivileged UserOperation sender who times a fill against real-time market data during that staleness window can pay for sponsored gas at a mispriced rate, draining paymaster treasury value on each occurrence.

### Finding Description
`_getOraclePrice` fetches the last reported round for both the native/USD and token/USD feeds and only validates that the answer is positive and not older than `maxOracleAge`: [1](#0-0) 

`_tokenPrice` combines the two stale-but-"fresh-enough" readings directly into the amount of ERC-20 token charged per unit of gas, with only a governance-set `markupBps` (default 2%, capped at 50%) as a buffer: [2](#0-1) 

`maxOracleAge` is validated only against a hard ceiling of 7 days, and the deployment script defaults it to ~25 hours specifically to tolerate typical Chainlink stablecoin heartbeats: [3](#0-2) [4](#0-3) 

This is exactly the failure mode the referenced report warns about: `latestRoundData()` returns the last *pushed* update, not the live price, and a wide tolerated staleness window (hours to days) means the on-chain price can materially diverge from the real market price for that entire window before a heartbeat or deviation-threshold push corrects it. Any solver/user paying gas through this paymaster (mode `0x00` permit or `0x02` Permit2) can watch off-chain spot prices and submit a UserOperation only when the on-chain stale price undercharges relative to the real price (e.g. native asset spot price has risen, or the token's spot price has fallen, since the last on-chain push), extracting the difference from the paymaster's treasury on that fill. This is a single, unprivileged transaction (`prepareBidUserOp`/`_executePermit` path used by every Simplex intent filler), requiring no compromise of governance, relayer, or any other privileged role.

### Impact Explanation
Every gas-sponsored UserOperation processed while the oracle is stale is priced against a market snapshot that can be materially wrong for up to the full `maxOracleAge` window (default ~25h, governance-extendable to 7 days). Since this paymaster is the gas-sponsorship mechanism used by Simplex intent fillers/solvers to submit bids on Hyperbridge intents, an attacker can systematically time fills to capture the spread between the stale charged price and the true market price, draining the paymaster's `markupBps` buffer and ultimately its EntryPoint deposit / token float — real, ongoing theft of protocol treasury funds, not a one-off griefing loss.

### Likelihood Explanation
High: the exploit requires only watching a public price feed off-chain and choosing when to submit an otherwise-normal UserOperation; no special privileges, front-running infrastructure, or governance access are needed. The deployed `maxOracleAge` default (~25h) and configurable ceiling (7 days) both comfortably exceed the time needed for typical crypto volatility to exceed the 2% default `markupBps` buffer.

### Recommendation
Do not treat `latestRoundData()`'s `updatedAt` bound alone as sufficient freshness. Either (a) tighten `maxOracleAge` to the feed's actual heartbeat with minimal slack, (b) add a secondary sanity check against a second independent price source (e.g. a TWAP or a redundant feed) and reject/clamp when they diverge beyond a small tolerance, or (c) increase `markupBps` to conservatively cover plausible price drift over `maxOracleAge`, sized to the feed's realistic volatility rather than a flat 2%.

### Proof of Concept
1. Observe that a registered token's Chainlink feed (or the native/USD feed) has not pushed an update for close to `maxOracleAge` while the real market price has moved by more than `markupBps` (2% default) in the paymaster's favor being underpriced.
2. Build and submit a UserOperation through `SimplexPaymaster` (mode `0x00`/`0x02`) that pays gas in the affected token; `_getOraclePrice` at `evm/src/utils/SimplexPaymaster.sol:662-676` accepts the reading because `block.timestamp - updatedAt <= maxOracleAge`.
3. `_tokenPrice` (`evm/src/utils/SimplexPaymaster.sol:653-658`) computes a token charge below the true market-equivalent cost of the sponsored gas; the difference is captured by the sender at the paymaster treasury's expense.
4. Repeat across every stale window to accumulate losses to the paymaster.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L361-365)
```text
        if (p.treasury == address(0)) revert ZeroAddress();
        if (p.markupBps > MAX_MARKUP_BPS) revert InvalidMarkup(p.markupBps);
        if (p.maxOracleAge == 0 || p.maxOracleAge > MAX_ORACLE_AGE) revert InvalidOracleAge(p.maxOracleAge);
        if (p.swapSlippageBps > MAX_SWAP_SLIPPAGE_BPS) revert InvalidSlippage(p.swapSlippageBps);

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

**File:** evm/script/DeploySimplexPaymaster.s.sol (L18-21)
```text
        // Stablecoin feeds on Ethereum and Base run a 24h heartbeat; a buffer over
        // 24h avoids transient StaleOraclePrice reverts on late pushes.
        uint256 maxOracleAge = vm.envOr("MAX_ORACLE_AGE", uint256(90_000));
        uint256 swapSlippageBps = vm.envOr("SWAP_SLIPPAGE_BPS", uint256(200)); // default 2%
```
