I have sufficient context to confirm the analog vulnerability.

The `SimplexPaymaster` contract uses a single `maxOracleAge` threshold to validate staleness for both the `nativeOracle` feed and every registered token's `tokenOracle` feed, exactly mirroring the JOJO `chainlinkAdaptor` M-12 bug class. This is reachable by any unprivileged user submitting an ERC-4337 UserOperation through the paymaster's `_fetchDetails`/`_tokenPrice`/`_getOraclePrice` path during `validatePaymasterUserOp`, making the paymaster's gas-fee pricing an unprivileged, transaction-reachable path (analogous to a "bandwidth purchaser"). [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Single `maxOracleAge` staleness bound shared across native-asset and per-token Chainlink feeds enables stale-price exploitation or DoS in `SimplexPaymaster` - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster` stores exactly one global staleness bound, `maxOracleAge`, and applies it identically when validating both the `nativeOracle` (e.g., BNB/USD, ETH/USD) and every registered `TokenConfig.tokenOracle` (e.g., USDC/USD, USDT/USD) in `_getOraclePrice`. This is the same root cause as JOJO's M-12: Chainlink heartbeats differ materially by feed (stablecoin feeds often update on a ~24h heartbeat while volatile native-asset feeds update on a ~1h or shorter heartbeat), so one shared threshold cannot be correct for both.

### Finding Description
`_getOraclePrice` is called twice per pricing operation — once for `nativeOracle` and once for `cfg.tokenOracle` — both gated by the same `maxOracleAge`: [1](#0-0) 

`maxOracleAge` is a single contract-wide parameter set via governance `UpdateParams`/`initialize`, with no per-oracle or per-feed-type staleness values: [3](#0-2) [4](#0-3) 

The contract's own documentation acknowledges heartbeats vary widely across chains and tokens ("BSC stablecoins ~27s, Base/Ethereum stablecoins up to 24h"), yet only a single bound is enforced for the native/gas-asset feed and every registered ERC-20 feed simultaneously: [2](#0-1) 

This value directly drives `_tokenPrice`, which is used in the reachable, unprivileged path `_fetchDetails` → `_tokenPrice` → `_getOraclePrice`, invoked during every paymaster-sponsored `validatePaymasterUserOp`/`postOp`, and also in `swapAndDeposit`'s minimum-output calculation: [5](#0-4) [6](#0-5) 

### Impact Explanation
If `maxOracleAge` is set tight enough to suit the fast-heartbeat native-asset feed, then the slower-heartbeat stablecoin `tokenOracle` will routinely appear stale, causing `StaleOraclePrice` reverts and near-constant denial of service for any user attempting to pay gas with that token (loss of availability for the paymaster's core function). Conversely, if `maxOracleAge` is set loose enough to accommodate the slow stablecoin heartbeat, the fast-moving native-asset price can be accepted many multiples of its intended heartbeat out of date. Since `_tokenPrice` computes `(nativeUsd * tokenDecimals * (10000+markup)) / (tokenUsd * 10000)`, a stale, off-market `nativeUsd` directly under- or over-prices the ERC-20 amount charged to UserOp senders relative to the true gas cost, letting users underpay (draining paymaster funds/treasury value) or overpay. The same stale `nativeUsd`/`tokenUsd` pair also sets `amountOutMin` in `swapAndDeposit`, degrading the slippage protection meant to prevent execution-price manipulation during fee-recycling swaps.

### Likelihood Explanation
This condition is highly likely to materialize whenever governance configures `maxOracleAge` without separately tracking the actual heartbeat of each configured feed, exactly as happened in the JOJO incident. No attacker action is required beyond simply using the paymaster during a period where feed update cadences diverge from the configured threshold; any ordinary UserOp sender interacting with `validatePaymasterUserOp`/`postOp` can trigger the mispriced path once such a window occurs.

### Recommendation
Track a separate maximum staleness bound per oracle (e.g., store `maxOracleAge` alongside `tokenOracle` in `TokenConfig`, and a distinct one for `nativeOracle`), matching each configured feed's actual Chainlink heartbeat rather than sharing one global value across feeds with different update cadences.

### Proof of Concept
1. Governance configures `nativeOracle` = ETH/USD (heartbeat ~3600s) and registers `tokenOracle` = USDC/USD (heartbeat up to 86400s) via `initialize`/`RegisterToken`.
2. Governance sets `maxOracleAge` to a single value, e.g. 3600s, to keep the native feed check tight.
3. USDC/USD legitimately goes ~4 hours without a new round (well within Chainlink's normal 24h heartbeat behavior).
4. Any user's `validatePaymasterUserOp` call now reverts with `StaleOraclePrice` on the token leg via `_getOraclePrice`/`_tokenPrice`/`_fetchDetails`, even though the USDC feed is not actually stale by its own heartbeat — denial of service for that token.
5. Alternatively, if governance instead sets `maxOracleAge` to 86400s to accommodate USDC/USD, then a UserOp submitted during a native-asset flash-crash window where `nativeOracle` hasn't updated in, say, 6 hours (within the loose 86400s bound but far outside ETH/USD's real ~3600s heartbeat) is priced against a stale `nativeUsd`, letting the user pay a stale (and potentially much cheaper) rate for gas relative to current market price.

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

**File:** evm/src/utils/SimplexPaymaster.sol (L196-200)
```text
    AggregatorV3Interface public nativeOracle;
    uint8 public nativeOracleDecimals;
    uint256 public maxOracleAge;
    uint256 public markupBps;
    address public treasury;
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

**File:** evm/src/utils/SimplexPaymaster.sol (L464-467)
```text
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;
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

**File:** evm/src/utils/SimplexPaymaster.sol (L653-676)
```text
    function _tokenPrice(TokenConfig memory cfg) internal view returns (uint256) {
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);

        return (nativeUsd * (10 ** cfg.tokenDecimals) * (10_000 + markupBps)) / (tokenUsd * 10_000);
    }

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
