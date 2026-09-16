### Title
Single global `maxOracleAge` staleness bound is too coarse for oracles with much tighter heartbeats, letting bandwidth purchasers exploit stale prices - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster` uses one governance-configured `maxOracleAge` value to bound staleness for *every* Chainlink feed it reads — the `nativeOracle` and every registered token's `tokenOracle` — even though these feeds have very different heartbeats (the contract's own comments cite "BSC stablecoins ~27s, Base/Ethereum stablecoins up to 24h"). Because the same threshold (capped only by `MAX_ORACLE_AGE = 7 days`) is applied uniformly, sizing it to tolerate the slowest feed makes it far too permissive for faster-heartbeat feeds, exactly analogous to the reported `MAX_TIME_GAP` issue.

### Finding Description
`maxOracleAge` is a single contract-wide parameter enforced identically for all oracles in `_getOraclePrice`: [1](#0-0) 

It is set once via `_setParams`, bounded only by the constant `MAX_ORACLE_AGE`: [2](#0-1) [3](#0-2) 

The `Params` struct and its own doc comment acknowledge that heartbeats differ drastically per oracle/chain, yet only one `maxOracleAge` field exists to bound them all: [4](#0-3) 

The deploy script confirms this is sized for the slowest feed (stablecoins, up to 24h) and deliberately padded above it: [5](#0-4) 

Because `_getOraclePrice` is invoked for both `nativeOracle` (fast heartbeat, e.g. ~27s on BSC) and every `tokenOracle` (potentially slow heartbeat, e.g. 24h) with the *same* `maxOracleAge`, a value chosen to avoid false StaleOraclePrice reverts on the slow stablecoin feed leaves the fast native-asset feed effectively unchecked for staleness over a window thousands of times longer than its real heartbeat. This directly mirrors the reported flaw: a single freshness bound set generously enough for the least-frequently-updated feed silently defeats the staleness check for feeds that update far more often and whose price can move meaningfully within that same window.

This price is read on every gas-sponsored user operation, via the unprivileged, permissionless entry point: [6](#0-5) [7](#0-6) 

### Impact Explanation
Any bandwidth purchaser (ERC-4337 UserOp sender using this paymaster) can have their gas cost priced against `_tokenPrice`, which combines `nativeUsd` and `tokenUsd`, both accepted as "fresh" as long as they are within `maxOracleAge` — regardless of the oracle's actual heartbeat. If the native asset's real feed heartbeat is much shorter than `maxOracleAge` (as documented in the code itself: 27s vs. a ~24h-sized bound), a native price update can lag by up to `maxOracleAge` without ever tripping `StaleOraclePrice`. During a native-asset price swing within that stale window (e.g., a market crash or a feed outage), a UserOp sender can submit operations priced off a favorably stale `nativeUsd`/`tokenUsd` ratio, systematically underpaying the paymaster relative to the true market price of gas. Since `PaymasterERC20` prefunds and settles based on this manipulable `tokenPrice`, the paymaster (and ultimately its treasury/EntryPoint deposit) bears the resulting loss — an unprivileged, directly reachable path to draining paymaster value over repeated stale-price submissions.

### Likelihood Explanation
No privileged action is required to trigger the exploit path itself — governance only needs to set `maxOracleAge` to a single, reasonable-looking value that accommodates the slowest registered oracle (the deploy script already demonstrates this exact pattern), which is a normal, non-malicious operational choice, not an attack. Any user submitting a UserOp through the paymaster during a period where the fast oracle is stale relative to its true heartbeat (but still within `maxOracleAge`) can exploit the mispriced conversion. This requires only a single UserOp submission, making it easily and repeatedly triggerable whenever such a price/heartbeat mismatch window opens.

### Recommendation
Track and enforce a per-oracle staleness bound instead of one contract-wide `maxOracleAge`. Store a `maxAge` alongside each `TokenConfig` and alongside `nativeOracle` (e.g. extend `Params`/`TokenConfig` with an oracle-specific field), validated against realistic heartbeats for that specific feed/chain at registration time, and check each oracle's own bound in `_getOraclePrice` rather than a single global constant capped only by `MAX_ORACLE_AGE`.

### Proof of Concept
1. Governance calls `UpdateParams` with `maxOracleAge` set to `86400` (or any value near `MAX_ORACLE_AGE`) to comfortably cover a slow stablecoin `tokenOracle` heartbeat (e.g., 24h), as the deploy script itself does (`evm/script/DeploySimplexPaymaster.s.sol:16-21`).
2. `nativeOracle` (e.g., BNB/USD with a ~27s heartbeat) stops updating for several hours due to sequencer lag, an oracle node outage, or simply because Chainlink's deviation threshold isn't crossed while the true market price moves.
3. A UserOp sender submits a UserOp through `validatePaymasterUserOp` → `_fetchDetails` → `_tokenPrice` → `_getOraclePrice`, using the now-stale-but-not-reverting `nativeOracle` answer (`evm/src/utils/SimplexPaymaster.sol:662-668`), obtaining a `tokenPrice` computed from an outdated native/USD rate.
4. The sender pays gas in the ERC-20 token at the favorably stale conversion rate; `PaymasterERC20` settles the prefund at this rate, so the paymaster's treasury systematically absorbs the difference between the stale and real market rate, repeatable for every UserOp sent during the stale window.

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

**File:** evm/src/utils/SimplexPaymaster.sol (L161-168)
```text
    /// @dev Hard cap on the governance-configurable markup (50%).
    uint256 public constant MAX_MARKUP_BPS = 5_000;

    /// @dev Hard ceiling on the governance-configurable oracle staleness bound.
    uint256 public constant MAX_ORACLE_AGE = 7 days;

    /// @dev Hard cap on the governance-configurable swap slippage (10%).
    uint256 public constant MAX_SWAP_SLIPPAGE_BPS = 1_000;
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

**File:** evm/src/utils/SimplexPaymaster.sol (L524-556)
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

**File:** evm/src/utils/SimplexPaymaster.sol (L660-668)
```text
    /// @dev Fetch a Chainlink price normalized to 8 decimals.
    ///      Reverts on stale or non-positive answers.
    function _getOraclePrice(AggregatorV3Interface oracle, uint8 oracleDecimals) internal view returns (uint256) {
        (, int256 answer,, uint256 updatedAt,) = oracle.latestRoundData();

        if (answer <= 0) revert InvalidOraclePrice(address(oracle), answer);
        if (block.timestamp - updatedAt > maxOracleAge) {
            revert StaleOraclePrice(address(oracle), updatedAt);
        }
```

**File:** evm/script/DeploySimplexPaymaster.s.sol (L16-21)
```text
        uint256 markupBps = vm.envOr("MARKUP_BPS", uint256(200)); // default 2%
        address treasury = vm.envOr("TREASURY", admin); // default to deployer
        // Stablecoin feeds on Ethereum and Base run a 24h heartbeat; a buffer over
        // 24h avoids transient StaleOraclePrice reverts on late pushes.
        uint256 maxOracleAge = vm.envOr("MAX_ORACLE_AGE", uint256(90_000));
        uint256 swapSlippageBps = vm.envOr("SWAP_SLIPPAGE_BPS", uint256(200)); // default 2%
```
