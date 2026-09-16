Confirmed: no `minAnswer`/`maxAnswer` circuit-breaker check exists anywhere in the codebase. The only Chainlink price consumption in a production contract is `_getOraclePrice` in `SimplexPaymaster.sol`, which validates only positivity and staleness.

### Title
Missing Chainlink circuit-breaker (`minAnswer`/`maxAnswer`) validation in `SimplexPaymaster._getOraclePrice` allows mispriced gas payments during extreme price moves - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster` is a permissionless ERC-4337 v0.8 paymaster that sponsors gas for any `UserOperation` in exchange for ERC-20 stablecoins (or any registered token), pricing the exchange rate via two Chainlink `AggregatorV3Interface` feeds (`nativeOracle` and each token's `tokenOracle`). Any unprivileged account can submit a `UserOperation` through mode `0x00` (permit) or `0x02` (Permit2) that triggers this pricing path, making the oracle-consumption logic reachable by any user without permission, similar to a message dispatcher/relayer fee-accounting entry point. [1](#0-0) 

### Finding Description
`_getOraclePrice` fetches `latestRoundData()` from the configured Chainlink aggregator and only guards against a non-positive answer and staleness (`updatedAt` older than `maxOracleAge`). It never checks whether the returned `answer` sits at the aggregator's configured `minAnswer`/`maxAnswer` circuit-breaker boundaries: [2](#0-1) 

Both `_tokenPrice` (used in `_validatePaymasterUserOp` → `PaymasterERC20` prefund calculation and in `estimateTokenCost`/`getTokenPrice`) and `swapAndDeposit` (fee-recycling swap sizing) consume `_getOraclePrice` for both `nativeOracle` and `cfg.tokenOracle` without any boundary check: [3](#0-2) [4](#0-3) 

If the underlying Chainlink aggregator for either the native asset or a registered token hits its internal circuit breaker (e.g. after a flash-crash such as the LUNA/UST collapse referenced in the source report), `latestRoundData()` continues returning the clamped `minAnswer`/`maxAnswer` value rather than reverting or signalling staleness. Since the price is still positive and `updatedAt` keeps advancing on subsequent heartbeats, both of `SimplexPaymaster`'s checks pass, and the contract silently uses the stale, boundary-clamped price as ground truth.

### Impact Explanation
`_tokenPrice` computes `tokenAmountOwed = nativeUsd * tokenDecimals * (10000+markupBps) / (tokenUsd * 10000)`. If `tokenUsd` (the token's USD price from its clamped oracle) is stuck above the real market price during a token collapse, the computed token amount charged to the UserOperation sender is understated relative to the real cost of the gas sponsored — the paymaster sponsors real ETH/BNB-denominated gas but is repaid in a rapidly depreciating, near-worthless token still valued at its `minAnswer` floor. An attacker (or any user) can repeatedly submit UserOperations paying with the near-zero-value collapsing token, draining the paymaster's `EntryPoint` deposit and treasury reserves funded by other users' fees — a direct value-extraction/theft scenario against protocol-held funds. Conversely, if `nativeOracle` is the one clamped upward, ordinary users are systematically overcharged. `swapAndDeposit` is similarly exposed: it sizes `amountOutMin` off the same unclamped price pair, so if `tokenUsd` is clamped high, the treasury-gated swap can be pushed to accept an unfavorable execution price without reverting, since the (already skewed) expected output shrinks the effective slippage protection.

### Likelihood Explanation
This requires an actual Chainlink aggregator hitting its configured min/max circuit breaker — a rare but historically observed event for volatile ERC-20 collateral (e.g. depegging/collapsing tokens). Because `SimplexPaymaster` explicitly documents it is designed to accept "USDC, USDT, or any token with a Chainlink feed," governance-added tokens beyond blue-chip stablecoins increase this likelihood. Once triggered, exploitation requires no special privilege: any account can submit `UserOperation`s against a live bundler using the depressed/frozen token, so likelihood of exploitation once the precondition (circuit-breaker trip) occurs is high, and detection would require independent price monitoring that this contract does not perform.

### Recommendation
In `_getOraclePrice`, fetch and cache the aggregator's `minAnswer`/`maxAnswer` (via `AggregatorV2V3Interface` extended calls or a governance-supplied bound per `TokenConfig`/`nativeOracle`), and revert (e.g. a new `OraclePriceOutOfBounds` error) whenever `answer <= minAnswer || answer >= maxAnswer`. Alternatively, allow governance to configure a secondary/fallback oracle without circuit breakers for tokens flagged as high-risk, and require `_registerToken`/`_setParams` to record these bounds so the check can be enforced generically for both `nativeOracle` and every `TokenConfig.tokenOracle`.

### Proof of Concept
1. Governance registers a token `T` via `_registerToken` with a Chainlink `tokenOracle` that has `minAnswer = $1` (per [5](#0-4) ).
2. `T`'s real market price collapses to `$0.01`, but the aggregator, hitting its floor, keeps reporting `answer = 1e8` (i.e., `$1` at 8 decimals) with `updatedAt` continuing to tick forward on each heartbeat.
3. `_getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals)` returns `1e8` — passing both the `answer <= 0` and `StaleOraclePrice` checks in [6](#0-5) .
4. An attacker submits a `UserOperation` with `paymasterData` mode `0x00`/`0x02` referencing token `T`. `_validatePaymasterUserOp` → `_tokenPrice` charges the attacker as if `T` were still worth `$1`, letting them pay ~100x less value than the sponsored gas actually costs.
5. Repeating this drains the paymaster's `EntryPoint` deposit/treasury funded by legitimate fee payers, with no revert or safeguard anywhere in the pricing path.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L53-67)
```text
/// @title  SimplexPaymaster
/// @author Polytope Labs
/// @notice Fully onchain, permissionless ERC-4337 v0.8 paymaster that accepts
///         ERC-20 stablecoins (USDC, USDT, or any token with a Chainlink feed)
///         for gas payment. Deployed behind an ERC1967Proxy and administered
///         exclusively through Hyperbridge governance.
///
/// Modes (byte 0 of paymasterData):
///   0x00  PERMIT  — EIP-2612 permit signature included; the permit is executed
///                    during validation so the subsequent prefund transferFrom
///                    succeeds without a prior onchain approval.
///   0x02  PERMIT2 — Permit2 SignatureTransfer signature included; the prefund
///                    is pulled through Permit2.permitTransferFrom, so the token
///                    only needs a one-time approval to Permit2 (the path for
///                    tokens without permit support, e.g. BSC stablecoins).
```

**File:** evm/src/utils/SimplexPaymaster.sol (L387-404)
```text
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
