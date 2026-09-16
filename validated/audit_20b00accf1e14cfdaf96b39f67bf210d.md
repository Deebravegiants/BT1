### Title
Governance-configurable Chainlink oracle staleness bound in `SimplexPaymaster` permits a 7-day-old price to size gas payments - ([File: evm/src/utils/SimplexPaymaster.sol])

### Summary
`SimplexPaymaster` prices ERC-4337 gas payments using two Chainlink feeds (native/USD and token/USD) via `_getOraclePrice`, which only rejects an answer if it is negative/zero or older than `maxOracleAge`. `maxOracleAge` is a governance-settable parameter bounded only by `MAX_ORACLE_AGE = 7 days`, and the comment in the `Params` struct explicitly notes some chains are configured with staleness windows "up to 24h" — the same order of magnitude flagged in the referenced Sherlock finding as dangerously permissive for a stale-price check.

### Finding Description
`_getOraclePrice` is the sole freshness gate on both price feeds used by the paymaster: [1](#0-0) 

`maxOracleAge` is validated only against a hard ceiling of 7 days when governance updates parameters: [2](#0-1) 

and the field is explicitly documented as varying "up to 24h" per chain: [3](#0-2) 

`_tokenPrice`, which drives every gas-cost computation, calls `_getOraclePrice` for both the native-asset feed and the token feed and simply divides one by the other with no additional sanity/deviation check beyond the staleness bound: [4](#0-3) 

This is the same bug class as the Sherlock finding: a stale-price check window that is large enough (here, up to 24h in normal configuration, and governance can push it to a full 7 days without hitting any additional constraint) that a fast native-asset price move (e.g., a depeg or crash) within that window is invisible to the contract. Because both feeds are checked independently, a scenario where only one of the two feeds (native or token) stalls/pauses while the other keeps updating produces an internally inconsistent, badly stale cross-price that is still accepted for up to `maxOracleAge`.

### Impact Explanation
Any unprivileged account submitting a UserOperation that pays gas through this paymaster (mode `0x00` permit or `0x02` permit2) triggers `_tokenPrice`/`_getOraclePrice` during validation and `postOp` settlement. If the native asset (e.g., ETH/BNB) price moves sharply while a feed is stalled within the allowed staleness window:
- Users can be **overcharged** in ERC-20 tokens relative to the true gas cost, draining value from unprivileged permit signers to the treasury/paymaster.
- Conversely, if the token/USD feed stalls while the token depegs downward, the paymaster **undercharges**, letting users pay a token that has lost most of its value for real gas, draining the paymaster's own reserves/deposit over many operations.

This is a protocol-level, permissionless funds-flow issue reachable by any UserOperation sender, not requiring any privileged or malicious governance action — governance staying within its allowed, documented bounds (up to 24h, or up to the 7-day ceiling) is sufficient to expose the window.

### Likelihood Explanation
Chainlink feed pauses/staleness incidents (the exact precedent cited in the original report, e.g. UST) are a realistic external event, and the contract's own comments acknowledge staleness windows "up to 24h" are an intended, normal configuration — not a misconfiguration. No additional circuit breaker, deviation check, or pause mechanism exists beyond the single staleness timestamp comparison, so likelihood is driven purely by external oracle/market conditions rather than any contract misuse.

### Recommendation
Tighten `MAX_ORACLE_AGE` to a much smaller bound (e.g., minutes, matching feed heartbeats plus a small buffer) instead of 7 days, and consider cross-checking both feeds' `updatedAt`/`answer` deltas against a secondary source or price-deviation guard rather than relying solely on a single staleness timestamp per feed.

### Proof of Concept
1. Governance (acting within its documented, non-malicious bounds) sets `maxOracleAge` to 24h (as the code comments indicate is expected for some chains) via `UpdateParams`.
2. Chainlink's native/USD feed pauses/stalls at time T (e.g., during a market crash) while still within the allowed 23h59m window.
3. An unprivileged user submits a UserOperation paying gas with an ERC-20 token; `fetchDetails`/`validatePaymasterUserOp` call `_tokenPrice` → `_getOraclePrice`, which accepts the stale `updatedAt` since `block.timestamp - updatedAt <= maxOracleAge`.
4. The stale native price (e.g., reflecting a pre-crash valuation) is used to compute `_erc20Cost`, over- or under-charging the user's token relative to actual gas cost, transferring value away from the unprivileged UserOperation sender or draining the paymaster's ERC-20/native reserves.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L139-152)
```text
    struct Params {
        /// @notice Native asset / USD oracle (BNB/USD on BSC, ETH/USD on Ethereum, etc.)
        AggregatorV3Interface nativeOracle;
        /// @notice Markup in basis points (100 = 1%). Applied on top of the oracle price.
        uint256 markupBps;
        /// @notice Receives markup surplus and EntryPoint deposit withdrawals.
        address treasury;
        /// @notice Maximum oracle staleness. Chainlink heartbeats vary per chain
        ///         (BSC stablecoins ~27s, Base/Ethereum stablecoins up to 24h).
        uint256 maxOracleAge;
        /// @notice Slippage tolerance in basis points applied to the
        ///         oracle-derived expected output in {swapAndDeposit}.
        uint256 swapSlippageBps;
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L361-383)
```text
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
