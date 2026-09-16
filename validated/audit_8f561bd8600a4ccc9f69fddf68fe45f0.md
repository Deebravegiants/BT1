### Title
SimplexPaymaster prices ERC-20 gas payments from a single Chainlink feed with no price-deviation/depeg check, allowing stablecoin depegs to drain the paymaster's EntryPoint deposit — ([File: evm/src/utils/SimplexPaymaster.sol])

### Summary
`SimplexPaymaster` accepts stablecoins (USDC, USDT, "or any token with a Chainlink feed") as gas payment for ERC-4337 `UserOperation`s, converting the real ETH cost of gas into token units purely from a Chainlink `token/USD` feed and a `native/USD` feed. Like the reported `PriceFeed.sol` WBTC issue, the only safeguards are staleness (`maxOracleAge`) and a non-positive-answer check — there is no bound on how far the reported USD price is allowed to deviate from the token's true value (e.g. a $1 peg). If a registered token depegs downward while its oracle still reports a stale-but-fresh price near $1 (which is exactly how Chainlink stablecoin feeds with 0.5–1% deviation thresholds behave during a fast depeg), the paymaster undercharges gas relative to the real USD value it receives, subsidizing every sponsored `UserOperation` out of its own EntryPoint deposit until it is drained.

### Finding Description
`_tokenPrice` computes the ERC-20/gas exchange rate directly from two oracle reads with no sanity bound against the token's expected peg: [1](#0-0) 

`_getOraclePrice` only rejects a non-positive answer or a stale `updatedAt`; it never checks that the returned USD price is close to an expected reference (e.g., $1.00 ± threshold) for a stablecoin: [2](#0-1) 

This `tokenPrice` is used directly in `_fetchDetails` to size `prefundAmount`/`erc20Cost` for every UserOperation routed through the paymaster (both the standard `transferFrom` prefund path and the Permit2 path): [3](#0-2) [4](#0-3) 

Any registered token can be affected — the contract doc explicitly states it supports "USDC, USDT, or any token with a Chainlink feed," and registration/config is purely governance-driven (`_registerToken`), with no per-token deviation parameter: [5](#0-4) 

`Params.maxOracleAge` bounds staleness but nothing bounds price deviation, unlike the report's recommendation of a secondary oracle or deviation-triggered halt: [6](#0-5) 

### Impact Explanation
During a depeg event (a stablecoin trading below its $1 reference while its Chainlink feed is still within heartbeat and hasn't crossed its own deviation threshold, or briefly lags real market price), any user submitting a paymaster-sponsored `UserOperation` — a fully permissionless, unprivileged action — is charged `tokenPrice` computed from the stale, too-high USD valuation. The paymaster ends up collecting tokens worth materially less in real USD than the ETH gas it just paid out of its EntryPoint deposit (analogous to the report's "accumulation of bad debt" from mispriced collateral). Because the paymaster auto-recycles fees and refunds unused gas from the same collected tokens (`swapAndDeposit`), a sustained depeg systematically drains the paymaster's native EntryPoint stake/deposit — a protocol-funds loss reachable purely by ordinary UserOperation submission, not by any privileged or malicious-admin action.

### Likelihood Explanation
Stablecoin depegs are a recurring, externally-triggered market event (as the original report notes for WBTC/BTC); no attacker collusion with governance or relayers is required, and no malicious node/consensus assumption is needed. The condition is triggered simply by ordinary paymaster usage continuing during a depeg window, which is entirely plausible given Chainlink's deviation-threshold-based (not continuous) stablecoin feed updates.

### Recommendation
Add a price-sanity/deviation check in `_getOraclePrice` (or `_tokenPrice`) for pegged assets — e.g., reject or clamp prices deviating beyond a configurable basis-point threshold from the token's expected peg, and/or cross-check against a second independent price source (on-chain DEX TWAP) as the original report recommends, halting sponsorship for a token whose oracle price falls outside the accepted band instead of silently accepting it.

### Proof of Concept
1. Governance registers a stablecoin `T` (e.g., USDC) with its Chainlink `T/USD` oracle via `RegisterToken`.
2. `T` depegs to $0.95 in the open market; its Chainlink feed (heartbeat not yet elapsed, deviation threshold not yet crossed) still reports ~$1.00, which passes both `_getOraclePrice` checks (`answer > 0`, not stale).
3. A user submits a `UserOperation` paying gas in `T` via mode `0x00`/`0x02`. `_tokenPrice` computes `tokenPrice` using the stale $1.00 valuation instead of the real $0.95, so `prefundAmount` collected in `T` is worth ~5% less in real USD than the ETH `maxCost` the paymaster pays the EntryPoint.
4. Repeated across many UserOperations during the depeg window, the paymaster's EntryPoint deposit is drained faster than it is replenished by (devalued) token collections, mirroring the reported PriceFeed bad-debt scenario.

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

**File:** evm/src/utils/SimplexPaymaster.sol (L563-583)
```text
    function _prefund(
        PackedUserOperation calldata userOp,
        bytes32 userOpHash,
        IERC20 token,
        uint256 tokenPrice,
        address prefunder_,
        uint256 maxCost
    )
        internal
        override
        returns (bool prefunded, uint256 prefundAmount, address prefunder, bytes memory prefundContext)
    {
        bytes calldata data = userOp.paymasterData();
        if (uint8(data[0]) != 0x02) {
            return super._prefund(userOp, userOpHash, token, tokenPrice, prefunder_, maxCost);
        }

        (, uint256 permitAmount, uint256 nonce, uint256 deadline, uint8 v, bytes32 r, bytes32 s) =
            _parsePermit2Data(data);
        prefundAmount = _erc20Cost(maxCost, userOp.maxFeePerGas(), tokenPrice);
        if (prefundAmount > permitAmount) revert InsufficientPermitAmount(permitAmount, prefundAmount);
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
