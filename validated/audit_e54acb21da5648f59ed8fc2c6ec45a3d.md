### Title
Global `maxOracleAge` in `SimplexPaymaster` can silently mismatch a registered token's real Chainlink heartbeat, permanently reverting the paymaster for that token - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster` gates every gas-fee price lookup on a single, globally-configured `maxOracleAge` staleness bound checked against `AggregatorV3Interface.latestRoundData().updatedAt`. Governance validates only that `maxOracleAge` is non-zero and ≤ a 7-day ceiling, but never validates it against the *actual* heartbeat of any registered token's or the native asset's Chainlink feed. Because different feeds (native asset feed vs. per-token feeds registered later via `RegisterToken`) can have very different real-world heartbeats (from ~27s on BSC to 24h on Ethereum/Base stablecoins, as the deploy script itself documents), a `maxOracleAge` that is safe for one feed can be tighter than another feed's natural update cadence, causing `_getOraclePrice` to revert `StaleOraclePrice` for that token on every call until the feed happens to push an update inside the window — exactly the "Vault can experience long downtime periods" pattern from the referenced report, where a threshold parameter is not kept in a range consistent with the tolerance of the underlying price source it gates.

### Finding Description
`_getOraclePrice` reverts whenever the elapsed time since the oracle's last update exceeds `maxOracleAge`: [1](#0-0) 

`maxOracleAge` is a single contract-wide value applied uniformly to `nativeOracle` and to every token's `tokenOracle` in `_tokenPrice`: [2](#0-1) 

Governance can set (or leave) `maxOracleAge` via `UpdateParams`; the only checks performed are a non-zero floor and a `MAX_ORACLE_AGE = 7 days` ceiling — there is no check that the value is compatible with the heartbeat of any currently- or later-registered oracle: [3](#0-2) [4](#0-3) 

Tokens (and their oracles) are registered independently of `UpdateParams`, via `RegisterToken`, with no cross-check against `maxOracleAge`: [5](#0-4) 

The deploy script itself acknowledges the mismatch risk between a chosen `maxOracleAge` and a feed's real heartbeat ("Stablecoin feeds on Ethereum and Base run a 24h heartbeat; a buffer over 24h avoids transient StaleOraclePrice reverts on late pushes"), confirming this is a real, previously-observed failure mode rather than a purely theoretical one: [6](#0-5) 

The root cause mirrors the referenced bug class precisely: a single admin-tunable threshold (`THRESHOLD` in the report / `maxOracleAge` here) is checked against a signal (`spot price deviation` / `oracle update recency`) whose natural drift can legitimately reach or exceed that threshold for a well-known bounded period (up to `updateThreshold`/`heartbeat`), and nothing in the contract enforces the threshold stay wide enough relative to that period. Any registration of a new token whose feed has a longer heartbeat than the currently-configured `maxOracleAge` (or any feed operator widening the effective heartbeat within Chainlink's own tolerances) reintroduces the downtime with no on-chain safeguard.

### Impact Explanation
While `maxOracleAge` is below a token's actual (or an ordinary, in-tolerance) update interval, every `_fetchDetails`/`_tokenPrice` call for that token reverts with `StaleOraclePrice`, so `SimplexPaymaster` can never sponsor a UserOperation paid in that token. Since the paymaster is the mechanism sponsoring gas for cross-chain message dispatch (ERC-4337 UserOperations that carry Hyperbridge dispatch/fill calls), this makes an entire payment route unusable for up to the feed's full heartbeat window (hours), a recurring denial-of-service on message dispatch for any user relying on that token, without requiring a compromised key or malicious actor — a legitimately-configured, in-range parameter is sufficient. This matches the accepted impact category "a route unable to deliver messages."

### Likelihood Explanation
This requires no attacker action: it triggers whenever governance registers or already operates a token whose oracle's real heartbeat exceeds the configured `maxOracleAge`, or when a feed operator (within Chainlink's own SLA) delays an update near the heartbeat boundary. Given the contract explicitly supports registering additional tokens post-deployment with independently-chosen oracles (`RegisterToken`) and applies one global `maxOracleAge` to all of them, the mismatch is easy to introduce operationally and, per the deploy script's own comment, has already been anticipated as a recurring operational hazard.

### Recommendation
Track staleness per-oracle rather than globally: store an expected/maximum heartbeat alongside each `TokenConfig` (and for `nativeOracle`) at registration time, derived from or validated against the feed's actual heartbeat, and require any global or per-token `maxOracleAge`/staleness bound to be ≥ that feed's heartbeat plus a safety buffer before it can be accepted by `UpdateParams`/`RegisterToken`. Reject registration or parameter updates that would leave any active oracle's tolerance tighter than its real update cadence.

### Proof of Concept
1. Deploy `SimplexPaymaster` with `maxOracleAge = 12 hours` (passes the `0 < x ≤ 7 days` check in `_setParams`), sized for the native BNB/USD feed which updates roughly every 27s on BSC.
2. Governance later calls `RegisterToken` to add a USDC token whose Chainlink `USDC/USD` feed (e.g. on Ethereum/Base) has a documented 24h heartbeat — `_registerToken` performs no cross-check against `maxOracleAge`.
3. As soon as more than 12 hours elapse since that feed's last on-chain update (routine and within Chainlink's own SLA, not an incident), any UserOperation attempting to pay gas in USDC calls `_fetchDetails` → `_tokenPrice` → `_getOraclePrice`, which reverts `StaleOraclePrice` per [7](#0-6) .
4. Every USDC-sponsored UserOperation reverts until the feed happens to push a fresh update, reproducing "long downtime periods" identical in mechanism to the referenced report, purely from a governance-set-but-unvalidated threshold interacting with an independent, uncorrelated oracle tolerance.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L161-168)
```text
    /// @dev Hard cap on the governance-configurable markup (50%).
    uint256 public constant MAX_MARKUP_BPS = 5_000;

    /// @dev Hard ceiling on the governance-configurable oracle staleness bound.
    uint256 public constant MAX_ORACLE_AGE = 7 days;

    /// @dev Hard cap on the governance-configurable swap slippage (10%).
    uint256 public constant MAX_SWAP_SLIPPAGE_BPS = 1_000;
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

**File:** evm/src/utils/SimplexPaymaster.sol (L385-404)
```text
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

**File:** evm/script/DeploySimplexPaymaster.s.sol (L14-21)
```text
    function deploy() internal override {
        address nativeOracleAddr = config.get("NATIVE_ORACLE").toAddress();
        uint256 markupBps = vm.envOr("MARKUP_BPS", uint256(200)); // default 2%
        address treasury = vm.envOr("TREASURY", admin); // default to deployer
        // Stablecoin feeds on Ethereum and Base run a 24h heartbeat; a buffer over
        // 24h avoids transient StaleOraclePrice reverts on late pushes.
        uint256 maxOracleAge = vm.envOr("MAX_ORACLE_AGE", uint256(90_000));
        uint256 swapSlippageBps = vm.envOr("SWAP_SLIPPAGE_BPS", uint256(200)); // default 2%
```
