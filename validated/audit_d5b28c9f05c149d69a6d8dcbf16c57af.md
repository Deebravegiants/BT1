### Title
Hardcoded `MAX_ORACLE_AGE` ceiling of 7 days permits stale Chainlink prices in `SimplexPaymaster` gas pricing - ([File: evm/src/utils/SimplexPaymaster.sol])

### Summary
`SimplexPaymaster` prices ERC-20 gas payments from Chainlink `nativeOracle`/`tokenOracle` feeds, rejecting an update only if it is older than `maxOracleAge`. The governance-settable `maxOracleAge` is capped at a hardcoded `MAX_ORACLE_AGE = 7 days`, which is far longer than the actual heartbeat of the feeds it's meant to protect (the code's own comment says BSC stablecoins ~27s, Ethereum/Base up to 24h), so a permissionless UserOperation sender can get gas priced off a native/token price up to a week stale.

### Finding Description
`_getOraclePrice` only reverts if `block.timestamp - updatedAt > maxOracleAge`: [1](#0-0) 

`maxOracleAge` is bounded only by the constant `MAX_ORACLE_AGE = 7 days`: [2](#0-1) 

and `_setParams`, invoked both at `initialize` and on every `UpdateParams` governance request, enforces exactly that ceiling and nothing tighter: [3](#0-2) 

`_tokenPrice`, which every UserOperation's ERC-20 cost is computed from (`estimateTokenCost`, `getTokenPrice`, and the internal ERC-20 charge path), consumes both the native and token oracle prices through this same staleness gate: [4](#0-3) 

Any unprivileged account can submit an ERC-4337 `UserOperation` naming this paymaster; the contract has no way to force `maxOracleAge` below 7 days, so as long as a permitted config sits anywhere near that ceiling (the contract itself doesn't require it to be tightly bound to the feed's real heartbeat), a submitter can time a UserOperation to land while the oracle is legitimately stale (e.g. after an oracle outage, RPC lag, or simply a slow-moving stablecoin feed configured near the cap) but the native/token price has since moved materially. The paymaster will then compute `_tokenPrice` from the outdated rate rather than reverting.

### Impact Explanation
Gas sponsorship is priced entirely from `_tokenPrice`, which is fed by `_getOraclePrice`. If the true native-asset price has fallen since the last on-chain update while `maxOracleAge` still accepts it, submitters pay less ERC-20 token than the actual gas cost, draining the paymaster's EntryPoint deposit/native balance over time — a direct value-extraction/fund-drain vector against the paymaster's treasury, reachable by any permissionless UserOperation sender, not an admin or relayer. Conversely if price rose, users could be overcharged, but the drain-the-sponsor direction is the concrete theft path matching the reported bug class (stale price accepted for too long enabling economic exploitation).

### Likelihood Explanation
Likelihood is Medium: exploitation requires the oracle to actually go stale (feed outage, sequencer/RPC issue, or a feed configured with a heartbeat close to the 7-day cap) combined with real price movement during that window, and requires governance to have configured `maxOracleAge` loosely enough (up to 7 days) rather than tightly to each feed's heartbeat. Because the contract's own hard ceiling permits configurations up to 7 days regardless of the feed's real cadence, a misconfiguration or an atypical feed (e.g., one with an unusually long heartbeat) makes exploitation straightforward for any UserOp sender with no special privilege, and no additional on-chain signal distinguishes a "stale but within-window" price from a fresh one.

### Recommendation
Lower `MAX_ORACLE_AGE` to a value proportional to real Chainlink heartbeats (e.g., a few hours), or better, derive the enforced ceiling per-oracle from each feed's actual heartbeat/description rather than a single global 7-day hardcoded cap, and additionally sanity-check the price deviation against a secondary source (e.g., the Uniswap-based `swapSlippageBps` check already used elsewhere) before trusting a near-boundary-age price for pricing gas.

### Proof of Concept
1. Governance calls `UpdateParams` with `maxOracleAge` set to a value close to `MAX_ORACLE_AGE` (7 days) — this is accepted because `_setParams` only checks `maxOracleAge <= MAX_ORACLE_AGE` [5](#0-4) .
2. The configured Chainlink feed stalls (sequencer outage, oracle node failure) for several days while the underlying native-asset price drops materially.
3. Any user submits a `UserOperation` through the EntryPoint naming `SimplexPaymaster`; `_executePermit`/paymaster validation calls `_tokenPrice` → `_getOraclePrice`, which does not revert because `block.timestamp - updatedAt <= maxOracleAge` [6](#0-5) .
4. The user's ERC-20 payment is computed from the stale, now-overvalued native price, letting them pay less than the true gas cost, draining the paymaster's deposit at the expense of the treasury/governance-configured sponsor.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L161-166)
```text
    /// @dev Hard cap on the governance-configurable markup (50%).
    uint256 public constant MAX_MARKUP_BPS = 5_000;

    /// @dev Hard ceiling on the governance-configurable oracle staleness bound.
    uint256 public constant MAX_ORACLE_AGE = 7 days;

```

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
