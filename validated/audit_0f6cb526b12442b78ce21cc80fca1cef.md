The `SimplexPaymaster` contract is a strong analog for this bug class. It queries Chainlink `latestRoundData()` directly with no `try/catch`, so if the call reverts (feed paused, deprecated, or Chainlink admin access removed), the entire paymaster becomes permanently unusable.

### Title
Unhandled Chainlink `latestRoundData()` reverts in `SimplexPaymaster._getOraclePrice` cause permanent denial-of-service for gas-sponsored transactions - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster` sponsors gas for solvers/users paying in ERC-20 (e.g. USDC) by pricing the token via two Chainlink `AggregatorV3Interface.latestRoundData()` calls in `_getOraclePrice`, with no `try/catch` around the external call.

### Finding Description
Every `UserOperation` that uses this paymaster passes through `_fetchDetails`, which calls `_tokenPrice(cfg)` [1](#0-0) , which in turn calls `_getOraclePrice` twice (once for the native/USD feed, once for the token/USD feed) [2](#0-1) .

`_getOraclePrice` makes a bare, unprotected call to `oracle.latestRoundData()`:
```solidity
function _getOraclePrice(AggregatorV3Interface oracle, uint8 oracleDecimals) internal view returns (uint256) {
    (, int256 answer,, uint256 updatedAt,) = oracle.latestRoundData();
    ...
}
``` [3](#0-2) 

There is no `try/catch` wrapping this external call anywhere in the contract (confirmed by inspection of all revert paths in the file — only application-level checks like `InvalidOraclePrice`/`StaleOraclePrice` are guarded, not the call itself). If the underlying Chainlink registry reverts — e.g. the feed is deprecated/removed, access is restricted by Chainlink's multisig, or the aggregator is paused — `latestRoundData()` bubbles up an unhandled revert. Since `_fetchDetails` is invoked from `_validatePaymasterUserOp`'s parent flow (`PaymasterERC20._fetchDetails` override) and from view-only estimation entry points `getTokenPrice`/`estimateTokenCost` [4](#0-3) , this revert propagates and blocks:
- Validation of **every** `UserOperation` for **every** registered token (both `nativeOracle` and each token's oracle are queried unconditionally on each call).
- `_tokenPrice` is also used in `swapAndDeposit`'s fee-recycling flow [5](#0-4) , so fee recycling to keep the paymaster's EntryPoint deposit funded is blocked too.

The paymaster is described as the mechanism by which "solver accounts" and other users pay gas in stablecoins to fill cross-chain intents/orders [6](#0-5) . Any single unprivileged actor — a solver constructing a `UserOperation` to fill an intent, or any user submitting a UserOp through this paymaster — triggers the vulnerable code path, and an external oracle-side failure (outside contract control) then denies service to the entire paymaster for all users, not just the submitter.

### Impact Explanation
A reverting Chainlink feed permanently and indiscriminately blocks:
1. All gas-sponsored `UserOperation`s (mode `0x00` permit and mode `0x02` Permit2) for any registered token, since `_fetchDetails`/`_tokenPrice` always queries both `nativeOracle` and the per-token oracle.
2. Fee recycling via `swapAndDeposit`, starving the paymaster's EntryPoint deposit and eventually causing bundlers to stop accepting its sponsored ops entirely.

Recovery requires a governance round-trip (`UpdateParams`/`RegisterToken` via `onAccept`, gated to Hyperbridge governance) to swap in a working oracle — there is no permissionless self-healing path. This matches the "route unable to deliver messages"/permanent freezing analog: intent solvers relying on this paymaster to sponsor fills lose the ability to submit gas-sponsored fills until governance intervenes.

### Likelihood Explanation
Chainlink feeds can and do become unavailable (deprecation, multisig-controlled access revocation, feed migration) independent of any malicious actor in this system, and the contract explicitly acknowledges dependence on external oracle liveness via `maxOracleAge`/staleness checks — but only checks the *returned data*, not the possibility the call itself reverts. Because both oracles are read on every validation, a single stuck feed (even the token side, not just `nativeOracle`) suffices to halt the whole paymaster for that token, and since `nativeOracle` is shared across all tokens, its failure halts every token simultaneously.

### Recommendation
Wrap `oracle.latestRoundData()` in `_getOraclePrice` with `try/catch`, and on failure either (a) revert with an explicit `OraclePriceUnavailable` error surfaced early with a dedicated selector bundlers can filter on, or (b) fall back to a secondary/backup oracle if one is configured, so that a single feed outage does not permanently deny sponsorship for all tokens/users:
```solidity
function _getOraclePrice(AggregatorV3Interface oracle, uint8 oracleDecimals) internal view returns (uint256) {
    try oracle.latestRoundData() returns (uint80, int256 answer, uint256, uint256 updatedAt, uint80) {
        if (answer <= 0) revert InvalidOraclePrice(address(oracle), answer);
        if (block.timestamp - updatedAt > maxOracleAge) revert StaleOraclePrice(address(oracle), updatedAt);
        ...
    } catch {
        revert OracleCallFailed(address(oracle));
    }
}
```
Additionally, consider allowing governance to register a fallback oracle per token to avoid full DoS from a single feed's failure.

### Proof of Concept
1. Governance registers `tokenA` with `tokenOracle = feedA` via `RegisterToken`.
2. Chainlink's multisig (or feed deprecation) causes `feedA.latestRoundData()` to revert for all callers.
3. Any user/solver submits a `UserOperation` using `SimplexPaymaster` with `tokenA` (or any other registered token, since `nativeOracle` reverting has the same effect) — `_validatePaymasterUserOp` → `_fetchDetails` → `_tokenPrice` → `_getOraclePrice` reverts uncaught.
4. Every UserOp through this paymaster now reverts during validation; bundlers cannot include any sponsored operation. `getTokenPrice`/`estimateTokenCost` view calls also revert, breaking off-chain quoting used by the SDK's `GasEstimator` [7](#0-6) .
5. Service remains down until Hyperbridge governance delivers an `UpdateParams`/`RegisterToken` request with a working oracle.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L84-90)
```text
/// @dev Security model. The only allowance a solver ever holds towards this
///      contract is the residue of a mode 0x00 permit, bounded by the signed
///      permitAmount; mode 0x02 leaves none. A compromise must never translate
///      into large withdrawals from solver accounts. There is no privileged
///      key: every administrative action — upgrades, parameter changes, token
///      registry, withdrawals — is an onAccept request authenticated as
///      originating from Hyperbridge governance and delivered by the local
```

**File:** evm/src/utils/SimplexPaymaster.sol (L464-466)
```text
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
```

**File:** evm/src/utils/SimplexPaymaster.sol (L545-546)
```text
        tokenPrice = _tokenPrice(cfg);
        token = IERC20(tokenAddr);
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

**File:** evm/src/utils/SimplexPaymaster.sol (L682-697)
```text
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

**File:** sdk/packages/sdk/src/protocols/intents/GasEstimator.ts (L97-120)
```typescript
	/**
	 * Estimates the gas cost for a solver to fill the given order and returns
	 * a structured estimate with individual gas components and total costs in
	 * both wei and fee-token units.
	 *
	 * **Cross-chain orders:** also estimates the ISMP POST request fee required
	 * for the solver to trigger source-chain escrow redemption after filling, and
	 * includes it in `fillOptions.relayerFee`. The dispatch is always paid in the
	 * fee token — `nativeDispatchFee` is fixed at 0. The native rail would draw
	 * from the solver account's native balance, which nothing guarantees, and a
	 * shortfall is invisible to estimation (the account balance is overridden
	 * during simulation) — it would only surface as a reverted execution that
	 * still bills the paymaster.
	 *
	 * **Bundler path:** constructs a mock `PackedUserOperation` signed by an
	 * ephemeral keypair, applies state overrides, and calls
	 * `eth_estimateUserOperationGas`. Gas limits are bumped by 5-10% for
	 * headroom. If the bundler is Pimlico, gas prices are refined with
	 * `pimlico_getUserOperationGasPrice`.
	 *
	 * **Fallback path (no bundler):** uses a fixed budget
	 * ({@link NO_BUNDLER_FILL_GAS_BASE} plus {@link NO_BUNDLER_FILL_GAS_PER_OUTPUT}
	 * per output leg) — public RPCs don't reliably support estimation with
	 * state overrides.
```
