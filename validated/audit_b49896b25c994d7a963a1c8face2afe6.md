### Title
Single `maxOracleAge` staleness bound shared across all Chainlink price feeds in `SimplexPaymaster` causes DoS or stale-price mispricing - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster` prices ERC-20 gas payments using two Chainlink `AggregatorV3Interface` feeds — `nativeOracle` and each token's `TokenConfig.tokenOracle` — but validates the staleness of every feed against one global `maxOracleAge` value [1](#0-0) . Chainlink heartbeats differ per asset and per chain (the contract's own comment notes "BSC stablecoins ~27s, Base/Ethereum stablecoins up to 24h") [2](#0-1) , so one bound cannot correctly validate multiple oracles with materially different actual update cadences — the exact bug class described in the Sherlock report for `PoolGetters::getAssetPrice`.

### Finding Description
`Params.maxOracleAge` is a single governance-set value applied uniformly to the native/USD oracle and to every registered token/USD oracle [3](#0-2) . Every pricing call — `_tokenPrice`, `getTokenPrice`, `estimateTokenCost`, and `swapAndDeposit` — funnels through `_getOraclePrice`, which reverts with `StaleOraclePrice` if `block.timestamp - updatedAt > maxOracleAge`, using the same threshold regardless of which oracle is being checked [4](#0-3) [5](#0-4) .

Tokens are registered independently via `RegisterToken` governance requests, each supplying its own `AggregatorV3Interface` with no per-token heartbeat parameter [6](#0-5) , so the deployment can end up with a native oracle and multiple token oracles that have genuinely different heartbeats (e.g. a fast native feed and a 24h stablecoin feed, or vice versa) all checked against the one `maxOracleAge`.

### Impact Explanation
- If `maxOracleAge` is tuned to the fast feed (as deployment scripts already anticipate — a comment references a 90,000s buffer specifically to avoid "transient StaleOraclePrice reverts on late pushes" for 24h stablecoin feeds [7](#0-6) ), any oracle whose true heartbeat exceeds that bound will systematically revert as stale. Every `_fetchDetails`/`getTokenPrice`/`estimateTokenCost` call for that token then reverts, so no `UserOperation` can be sponsored in that token: solvers relying on `SimplexPaymaster` for gas (bids, delegations, vault sweeps per `sdk/packages/simplex/docs/ai/flows/paymaster-selection-for-a-sponsored-userop.md`) are denied service and forced onto the native-gas fallback or fail entirely if they hold no native funds. This is a liveness/DoS on the sponsored-UserOp path for intent solvers/bandwidth purchasers.
- If instead `maxOracleAge` is loosened to tolerate the slowest oracle, faster-updating feeds lose meaningful staleness protection, letting genuinely stale prices be used to compute `tokenPrice`/`prefundAmount`, mispricing gas payments (solver over/under-charged, or the treasury's markup miscalculated) in `_prefund`/`swapAndDeposit`.

### Likelihood Explanation
Governance already configures a single global age per deployment and the codebase's own design notes acknowledge the tension (choosing 90,000s specifically to survive 24h feeds while the native/other feeds are much faster) [7](#0-6) . Any future `RegisterToken` for a token whose oracle heartbeat differs materially from the value chosen at deploy time reproduces the condition without any special conditions — no attacker action needed, just normal Chainlink feed behavior on a supported chain.

### Recommendation
Store a per-oracle staleness bound (native oracle and each `TokenConfig`) instead of one contract-wide `maxOracleAge`, and validate `_getOraclePrice` against the bound configured for that specific feed, mirroring the report's suggested mitigation of passing a heartbeat parameter alongside each oracle.

### Proof of Concept
1. Deploy `SimplexPaymaster` with `maxOracleAge` set to accommodate the native BNB/USD feed (~27s heartbeat on BSC), per `DeploySimplexPaymaster.s.sol` defaults.
2. Governance registers a stablecoin token whose Chainlink feed has a 24h heartbeat (as documented for USDT/USD on Ethereum/Linea-class chains).
3. Once more than `maxOracleAge` elapses without a ≥deviation-triggered update on that feed (normal, expected behavior for a 24h-heartbeat feed), any call to `getTokenPrice`, `estimateTokenCost`, `_fetchDetails` (in `_validatePaymasterUserOp`/paymaster validation), or `swapAndDeposit` for that token reverts with `StaleOraclePrice`, exactly as exercised in `testStaleOracleReverts`/`testUpdateParamsTightensOracleAge` [8](#0-7) , denying gas sponsorship for that token until the feed happens to update.

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

**File:** evm/src/utils/SimplexPaymaster.sol (L386-404)
```text
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

**File:** evm/src/utils/SimplexPaymaster.sol (L464-467)
```text
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;
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

**File:** evm/script/DeploySimplexPaymaster.s.sol (L18-20)
```text
        // Stablecoin feeds on Ethereum and Base run a 24h heartbeat; a buffer over
        // 24h avoids transient StaleOraclePrice reverts on late pushes.
        uint256 maxOracleAge = vm.envOr("MAX_ORACLE_AGE", uint256(90_000));
```

**File:** evm/tests/foundry/SimplexPaymasterTest.t.sol (L245-270)
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

    function testUpdateParamsTightensOracleAge() public {
        nativeOracle.setUpdatedAt(block.timestamp - 100);
        _updateParams(address(nativeOracle), 0, treasury, 50);
        vm.expectRevert();
        paymaster.getTokenPrice(address(usdc6));
    }
```
