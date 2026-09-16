### Title
Simplex Paymaster's shared native-price oracle causes total DOS of gas sponsorship for all IntentGateway solvers on a single stale/invalid Chainlink answer - ([File: evm/src/utils/SimplexPaymaster.sol])

### Summary
`SimplexPaymaster._tokenPrice()` computes the ERC-20 gas price for a UserOperation by chaining two independent Chainlink calls — `nativeOracle` and the per-token `cfg.tokenOracle` — through `_getOraclePrice()`, which reverts on any stale or non-positive answer. Because every registered token's price computation depends on the same shared `nativeOracle`, a single misbehaving oracle feed (stale timestamp or non-positive answer) reverts `_fetchDetails`/`_validatePaymasterUserOp` for **every** token and **every** solver using this paymaster, exactly the same "either-oracle-fails ⇒ whole call reverts" pattern described in the reference `OracleModule::_getPrice()` finding.

### Finding Description
`_tokenPrice()` fetches two prices and combines them with no fallback path: [1](#0-0) 

Each fetch reverts outright on staleness or a non-positive answer, with no secondary source or last-good-price fallback: [2](#0-1) 

`_tokenPrice()`/`_getOraclePrice()` is invoked from `_fetchDetails()`, which is called on every UserOperation validation (`_validatePaymasterUserOp` → `super._validatePaymasterUserOp` → `_fetchDetails`) and from the public views `getTokenPrice()`/`estimateTokenCost()`: [3](#0-2) [4](#0-3) 

Unlike `OracleModule`, this isn't two *redundant* sources for the same asset — `nativeOracle` and `tokenOracle` price different assets and are both mathematically required. But the bug-class match is precise: the function combines two independently-fallible external oracle reads with an all-or-nothing revert, and `nativeOracle` is a *single point of failure shared across every registered token*. A stale/misbehaving Chainlink feed for the native asset (or for any one token a solver happens to select) makes `_fetchDetails` revert for that path, and since `nativeOracle` is common to all tokens, one faltering feed halts sponsorship for the entire paymaster, not just the affected token.

### Impact Explanation
`SimplexPaymaster` is the ERC-4337 paymaster that Simplex solvers rely on to sponsor gas for the `SolverAccount` batched `select()`+`fillOrder()` UserOperations that fill IntentGateway orders (per `docs/content/developers/evm/intent-gateway/overview.mdx` and `docs/content/developers/evm/simplex/*`). If the shared `nativeOracle` (or the oracle backing whichever token a solver's tx targets) reports a stale timestamp or a non-positive answer, `_validatePaymasterUserOp`/`_fetchDetails` revert for every UserOperation routed through this paymaster. Bundlers cannot include any op sponsored by it, so solvers cannot fill outstanding cross-chain intent orders through the paymaster path while the feed is degraded — freezing user escrow on the source chain for the duration of the outage, mirroring the "keepers miss time-sensitive actions" impact in the original report. This is a Medium-severity DOS on an unprivileged, permissionless entry point (any solver submitting a UserOperation, or any user relying on solver fills), not a privileged-actor or monitoring-only issue.

### Likelihood Explanation
Chainlink feeds intermittently go stale or return non-positive answers during sequencer outages, feed deprecations, or extreme volatility guard triggers — a known, externally-triggerable (not attacker-controlled) condition also cited as the premise of the original finding. No special privilege is needed to trigger the revert: any solver's ordinary UserOperation submission during an oracle hiccup reverts, and because the check runs on every validation, it reliably blocks the whole paymaster rather than degrading gracefully. Likelihood is Medium — dependent on external oracle infrastructure health rather than an attacker action, matching the "Medium" original severity.

### Recommendation
Introduce a fallback/last-good-price mechanism instead of an unconditional revert in `_getOraclePrice()`/`_tokenPrice()`: cache the most recent valid price per oracle and use it (bounded by a wider staleness ceiling) when the live read fails, or support a secondary oracle per asset. At minimum, avoid a paymaster-wide single point of failure by allowing per-token pricing to degrade independently rather than all tokens sharing one unguarded `nativeOracle` call with no circuit breaker.

### Proof of Concept
1. A Chainlink aggregator backing `nativeOracle` (or any registered `TokenConfig.tokenOracle`) stops updating past `maxOracleAge`, or its `latestRoundData()` returns `answer <= 0` (both documented, reproducible conditions — see `testStaleOracleReverts`/`testNonPositiveOraclePriceReverts` in the test suite).
2. Any solver submits a UserOperation with `SimplexPaymaster` paymasterData for any registered token; the EntryPoint calls `_validatePaymasterUserOp` → `_fetchDetails` → `_tokenPrice` → `_getOraclePrice(nativeOracle, ...)`.
3. `_getOraclePrice` reverts with `StaleOraclePrice`/`InvalidOraclePrice`.
4. Because `nativeOracle` is shared, this reverts sponsorship for **every** token/every solver operation routed through the paymaster until the oracle recovers, confirmed by the existing tests: [5](#0-4)

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L524-547)
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

**File:** evm/src/utils/SimplexPaymaster.sol (L680-697)
```text
    /// @notice Current price in token base units per wei of gas (scaled by 1e18),
    ///         markup included. For offchain gas estimation.
    function getTokenPrice(address token) external view returns (uint256) {
        TokenConfig memory cfg = tokenConfigs[token];
        if (address(cfg.tokenOracle) == address(0)) revert TokenNotRegistered(token);

        return _tokenPrice(cfg);
    }

    /// @notice Estimate the token cost for a given gas amount and fee, mirroring
    ///         PaymasterERC20._erc20Cost (including its postOp gas cushion).
    function estimateTokenCost(address token, uint256 gasAmount, uint256 maxFeePerGas) external view returns (uint256) {
        TokenConfig memory cfg = tokenConfigs[token];
        if (address(cfg.tokenOracle) == address(0)) revert TokenNotRegistered(token);

        uint256 weiCost = gasAmount * maxFeePerGas + _postOpCost() * maxFeePerGas;
        return (weiCost * _tokenPrice(cfg)) / _tokenPriceDenominator();
    }
```

**File:** evm/tests/foundry/SimplexPaymasterTest.t.sol (L245-263)
```text
    function testStaleOracleReverts() public {
        nativeOracle.setUpdatedAt(block.timestamp - paymaster.maxOracleAge() - 1);
        vm.expectRevert(
            abi.encodeWithSelector(
                SimplexPaymaster.StaleOraclePrice.selector,
                address(nativeOracle),
                block.timestamp - paymaster.maxOracleAge() - 1
            )
        );
        paymaster.getTokenPrice(address(usdc6));
    }

    function testNonPositiveOraclePriceReverts() public {
        usdcOracle.setAnswer(0);
        vm.expectRevert(
            abi.encodeWithSelector(SimplexPaymaster.InvalidOraclePrice.selector, address(usdcOracle), int256(0))
        );
        paymaster.getTokenPrice(address(usdc6));
    }
```
