The strongest direct analog to the API3 heartbeat issue is in `SimplexPaymaster.sol`, which prices ERC-4337 gas payments off Chainlink feeds and reuses a single global staleness bound across oracles with very different heartbeats.

### Title
Single global `maxOracleAge` staleness bound is sized for the slowest feed, letting fast-heartbeat native-asset oracles be used while stale for up to that bound - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster` charges every UserOp sender (a "bandwidth purchaser" paying gas in ERC-20) by converting native gas cost to token cost via two Chainlink feeds (`nativeOracle` and each token's oracle), gated by one contract-wide `maxOracleAge` staleness bound [1](#0-0) . The contract's own documentation acknowledges that Chainlink heartbeats vary drastically per chain/feed - "BSC stablecoins ~27s, Base/Ethereum stablecoins up to 24h" [2](#0-1)  - yet only one `maxOracleAge` value is stored and applied identically to both the native/USD feed and every registered token/USD feed [3](#0-2) .

### Finding Description
`_getOraclePrice` reverts only if `block.timestamp - updatedAt > maxOracleAge`, using the single global bound for whichever oracle is passed in [1](#0-0) . `_tokenPrice` calls this same function for both `nativeOracle` and the token's oracle with the identical staleness threshold [4](#0-3) .

Because governance must pick one `maxOracleAge` that tolerates the slowest configured feed (the deploy script explicitly sets `MAX_ORACLE_AGE` to 90,000 seconds, i.e. 25 hours, specifically to avoid reverts from the 24h stablecoin heartbeat) [5](#0-4) , the *native* oracle - which per the contract's own comment can have a heartbeat as short as ~27 seconds on BSC - is permitted to be up to 25 hours stale before pricing reverts. Just as the API3 report warns that a 24h heartbeat means "the value update... can take slightly more than 24 hours" so callers must not assume freshness, here the contract does the opposite: it explicitly widens the acceptable staleness window for a fast-moving asset price to match a slow, unrelated feed, defeating the purpose of a heartbeat-based staleness check for that oracle.

`MAX_ORACLE_AGE` further hard-caps this at 7 days [6](#0-5) , so governance could legally configure an even larger window, and the validation in `_setParams` only checks `0 < maxOracleAge <= MAX_ORACLE_AGE`, with no per-oracle differentiation [7](#0-6) .

### Impact Explanation
Any unprivileged UserOp sender using this paymaster (mode 0x00 permit or 0x02 Permit2) is quoted a token price computed from `_tokenPrice`, which is directly exposed to a native-asset oracle answer that can legitimately be up to `maxOracleAge` (tens of hours) old [8](#0-7) . If the true native-asset price moves significantly within that staleness window (a realistic event for volatile assets like BNB/ETH over 24+ hours), a UserOp submitted near the end of the window is charged in ERC-20 tokens at a stale, favorable exchange rate relative to the live price, draining stablecoin reserves / EntryPoint deposit value from the paymaster (funds ultimately belonging to the treasury/protocol). This is a direct token-level fund loss reachable from a single permissionless transaction (a UserOp), consistent with the "bandwidth purchaser" attack surface explicitly in scope.

### Likelihood Explanation
Likelihood is elevated because: (1) the staleness window is intentionally widened via governance-configured `maxOracleAge` to accommodate the slowest feed, meaning under normal, non-malicious operation (not an oracle failure) the native oracle answer can sit near-stale for up to ~25 hours by design; (2) no additional sanity/deviation check exists beyond the single staleness bound and a `answer <= 0` check [1](#0-0) ; (3) any address can submit a UserOp through this paymaster (mode 0x00/0x02 paths are permissionless) and time it to exploit favorable stale pricing.

### Recommendation
Track a per-oracle (or at minimum per-role: native vs. token) staleness bound instead of one contract-wide `maxOracleAge`, sized to each feed's actual heartbeat rather than the slowest configured feed. Consider adding a secondary sanity check (e.g., bounding the max allowed price deviation between consecutive rounds, or requiring the native-asset feed's staleness bound to be materially tighter than stablecoin feeds) so that widening the bound for one feed cannot silently degrade freshness guarantees for another.

### Proof of Concept
1. Governance calls `UpdateParams` with `maxOracleAge = 90_000` (25h) to accommodate a 24h-heartbeat USDC/USD feed, as done in the deployment script [5](#0-4) .
2. The `nativeOracle` (e.g., BNB/USD, nominal heartbeat ~27s per the contract's own documentation comment) stops updating or lags for several hours due to normal network/keeper conditions, while its `updatedAt` is still within the 25h window.
3. The true BNB/USD price moves materially during this window (a realistic volatility event).
4. A user submits a UserOp through the paymaster; `_fetchDetails` → `_tokenPrice` → `_getOraclePrice` accepts the stale `nativeOracle` answer because `block.timestamp - updatedAt <= maxOracleAge` [1](#0-0) , charging the user (or crediting the attacker submitting many such ops) at the stale, mispriced rate and draining paymaster-held token/native value relative to fair market price.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L146-148)
```text
        /// @notice Maximum oracle staleness. Chainlink heartbeats vary per chain
        ///         (BSC stablecoins ~27s, Base/Ethereum stablecoins up to 24h).
        uint256 maxOracleAge;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L164-165)
```text
    /// @dev Hard ceiling on the governance-configurable oracle staleness bound.
    uint256 public constant MAX_ORACLE_AGE = 7 days;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L196-199)
```text
    AggregatorV3Interface public nativeOracle;
    uint8 public nativeOracleDecimals;
    uint256 public maxOracleAge;
    uint256 public markupBps;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L359-383)
```text
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

**File:** evm/src/utils/SimplexPaymaster.sol (L516-556)
```text
    /// @dev Returns the token to charge and its price relative to native gas.
    ///
    ///      PaymasterERC20 computes `erc20Cost = weiCost * tokenPrice / 1e18`,
    ///      so tokenPrice must be token base units per wei, scaled by 1e18:
    ///        tokenPrice = (nativeUsd * 10^tokenDecimals) / tokenUsd
    ///      e.g. BNB at $600, USDC at $1 with 6 decimals: 0.001 BNB (1e15 wei)
    ///      should cost 0.60 USDC (600000 units), giving tokenPrice = 6e8, which
    ///      is exactly (600e8 * 1e6) / 1e8. Markup is applied on top.
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

        if (mode == 0x02) {
            (,,, uint256 deadline,,,) = _parsePermit2Data(data);
            // Surfacing the permit deadline as validUntil lets bundlers drop
            // expiring ops instead of discovering it through a Permit2 revert.
            uint48 validUntil = deadline > type(uint48).max ? 0 : uint48(deadline);
            validationData = ERC4337Utils.packValidationData(true, 0, validUntil);
        }
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

**File:** evm/src/utils/SimplexPaymaster.sol (L662-668)
```text
    function _getOraclePrice(AggregatorV3Interface oracle, uint8 oracleDecimals) internal view returns (uint256) {
        (, int256 answer,, uint256 updatedAt,) = oracle.latestRoundData();

        if (answer <= 0) revert InvalidOraclePrice(address(oracle), answer);
        if (block.timestamp - updatedAt > maxOracleAge) {
            revert StaleOraclePrice(address(oracle), updatedAt);
        }
```

**File:** evm/script/DeploySimplexPaymaster.s.sol (L17-20)
```text
        address treasury = vm.envOr("TREASURY", admin); // default to deployer
        // Stablecoin feeds on Ethereum and Base run a 24h heartbeat; a buffer over
        // 24h avoids transient StaleOraclePrice reverts on late pushes.
        uint256 maxOracleAge = vm.envOr("MAX_ORACLE_AGE", uint256(90_000));
```
