### Title
Multi-token Chainlink price feed staleness in SimplexPaymaster allows unprivileged UserOp senders to underpay for gas across token markups - ([File: evm/src/utils/SimplexPaymaster.sol])

### Summary
`SimplexPaymaster` prices gas payment in any of several registered ERC-20 tokens using independent Chainlink `token/USD` feeds combined with a single `native/USD` feed [1](#0-0) . Each token's oracle has its own heartbeat/deviation characteristics, and the only safety check applied is a staleness cutoff (`maxOracleAge`), not a cross-token consistency or deviation check [2](#0-1) . This is structurally the same "intrinsic arbitrage" bug class as the Rio report: a protocol that normalizes/derives value across multiple assets purely from independently-updating Chainlink feeds, letting a caller who controls which asset they transact with exploit the feed that is currently lagging.

### Finding Description
`_tokenPrice` computes the amount of the chosen ERC-20 a UserOp must pay per unit of gas as `(nativeUsd * 10^tokenDecimals * (10000+markupBps)) / (tokenUsd * 10000)` [1](#0-0) . `_fetchDetails`, called during ERC-4337 validation for every submitted UserOperation, lets the caller freely pick `tokenAddr` from any registered/active token and prices gas exclusively off that token's own Chainlink feed at the current block [3](#0-2) . `_getOraclePrice` only rejects a feed answer that is non-positive or older than `maxOracleAge`; it applies no deviation bound relative to other feeds or any external reference [2](#0-1) .

Because `maxOracleAge` is a single global bound while Chainlink's actual update cadence per feed is driven by a heartbeat *and* a deviation threshold that varies by feed/chain (exactly the mechanism described in the Rio report), a registered token's feed can sit un-stale-by-timestamp yet be materially off the live market price (e.g., pending a +2% deviation-triggered update). An unprivileged UserOp sender — anyone who can submit a UserOperation through the EntryPoint/bundler — chooses which token to pay in, so they will preferentially pay through whichever registered token's feed currently underprices gas, extracting value from the paymaster's markup/treasury exactly as in the Rio deposit/withdraw arbitrage, except here the "deposit" and "withdrawal" sides are collapsed into a single gas-payment selection across N independently-priced tokens.

### Impact Explanation
Each mispriced UserOp silently reduces the effective markup (or drives it negative) captured by the paymaster/treasury, since the attacker is charged `tokenPrice` derived from a stale-but-not-timed-out feed. Because this can be repeated by any UserOp sender across every bundler-relayed operation, and the paymaster funds itself by staking with the EntryPoint and recycling collected token fees (`swapAndDeposit`) into native gas, sustained exploitation both erodes protocol revenue and can drain the paymaster's ability to remain solvent for its EntryPoint stake/deposit, a loss of value for the protocol consistent with a Medium/High-severity finding under the given scope (loss of value / unbacked payment discrepancy, not merely low/no-impact).

### Likelihood Explanation
Likelihood is moderate-to-high: no privileged access is required, exploitation only needs monitoring public Chainlink feeds for multiple registered tokens and submitting UserOps denominated in the currently-lagging token — the same publicly-documented and previously-exploited pattern cited in the Rio report (with on-chain evidence in the linked Twitter thread). It requires the paymaster to have ≥2 registered tokens with feeds of different update cadences/deviation thresholds, which is the paymaster's normal intended operating mode ("USDC, USDT, or any token with a Chainlink feed").

### Recommendation
- Do not rely solely on `maxOracleAge` staleness; also bound `_getOraclePrice`/`_tokenPrice` outputs against the last-known good price with a maximum-deviation check, or cross-validate the token/USD price against an independent source (TWAP from a DEX pool such as the existing `IUniswapV2Router02` integration already used in `swapAndDeposit`) before accepting it for gas pricing.
- Consider using a single reference conversion path (e.g., always route through native/USD and a TWAP-checked token/native pool) rather than trusting each token oracle's raw `latestRoundData()` independently.
- Track and cap per-token pricing drift between consecutive UserOps within a governance-configurable window to reduce the arbitrage window even if a feed is technically "fresh" by timestamp.

### Proof of Concept
1. Governance registers Token A (e.g., a stablecoin with a Chainlink feed with a wide 24h heartbeat / 0.5% deviation threshold) and Token B (feed with tighter parameters) in `SimplexPaymaster` [4](#0-3) .
2. The native asset's real market price moves such that Token A's feed has not yet been pushed on-chain (still within `maxOracleAge`, but off-market by up to its deviation threshold), while Token B's feed is current.
3. An attacker submits a UserOperation with `paymasterData` selecting Token A, causing `_fetchDetails` → `_tokenPrice` → `_getOraclePrice(cfg.tokenOracle, ...)` to compute gas cost off Token A's stale price [3](#0-2) .
4. The attacker pays materially less in USD-equivalent value than the actual gas cost + intended markup, repeating this every block the discrepancy persists, at no cost beyond normal UserOp submission.

Note: I was unable to fully trace whether `SimplexPaymaster` is deployed in production with more than one active token concurrently, or the exact governance-configured `maxOracleAge`/feed set per deployment, since those are runtime/config values set via `onAccept` governance requests rather than fixed in the contract; confirming real-world exploitability requires checking the live token registry and oracle configuration, which is outside what the indexed code provides.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L380-404)
```text
        treasury = p.treasury;
        maxOracleAge = p.maxOracleAge;
        swapSlippageBps = p.swapSlippageBps;
    }

    /// @dev Registers or updates a supported ERC-20 token with its token/USD feed.
    ///      Re-registering is also the recovery path for a misbehaving oracle.
    function _registerToken(address token, AggregatorV3Interface oracle) internal {
        if (token == address(0) || address(oracle) == address(0)) revert ZeroAddress();

        bool isNew = !tokenConfigs[token].active && address(tokenConfigs[token].tokenOracle) == address(0);

        tokenConfigs[token] = TokenConfig({
            tokenOracle: oracle,
            tokenOracleDecimals: oracle.decimals(),
            tokenDecimals: IERC20Metadata(token).decimals(),
            active: true
        });

        if (isNew) {
            registeredTokens.push(token);
        }

        emit TokenRegistered(token, address(oracle));
    }
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
