### Title
Chainlink oracle calls without try/catch in `SimplexPaymaster` can DoS ERC-20 gas sponsorship - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster._getOraclePrice` performs a direct, unguarded call to `AggregatorV3Interface.latestRoundData()` for both the native-asset and the ERC-20 token price feeds. Every ERC-20-denominated `UserOperation` processed by this paymaster (validation, prefund, and off-chain estimation) routes through this call. If either Chainlink feed reverts — which Chainlink's feed/aggregator multisig can trigger at will, as documented in the original report — the paymaster becomes permanently unable to validate or sponsor any UserOperation for any registered token, a total denial of service for the paymaster's gas-sponsorship route with no fallback or circuit breaker.

### Finding Description
`_getOraclePrice` calls Chainlink's `latestRoundData()` unconditionally, with no `try/catch`: [1](#0-0) 

This function is invoked from `_tokenPrice`, which is on the hot path of every ERC-20 gas payment: [2](#0-1) 

`_tokenPrice` (and therefore `_getOraclePrice`) is called from `_fetchDetails`, which runs during `_validatePaymasterUserOp` for **every** UserOperation that uses this paymaster to pay gas in an ERC-20 token: [3](#0-2) 

It is also invoked by `getTokenPrice` and `estimateTokenCost` (view helpers used for off-chain quoting) and by `swapAndDeposit` (fee-recycling), all of which revert under the same conditions: [4](#0-3) 

Any unprivileged user submitting a UserOperation that uses this paymaster ("bandwidth purchaser" paying for gas sponsorship) is affected. Because the oracle call has no defensive wrapper, a single blocked/paused Chainlink feed (native/USD or any registered token/USD) makes `_validatePaymasterUserOp` revert for every UserOperation across every registered token, since `nativeOracle` is queried unconditionally regardless of which token is being used to pay gas.

### Impact Explanation
This is a denial-of-service on the paymaster's core function: it can no longer sponsor gas for any user, for any registered ERC-20 token, until governance intervenes (deactivate/re-register the token or replace the oracle via governance-gated request kinds). Given that all pricing routes through the single `nativeOracle` in addition to the per-token oracle, a single compromised/paused feed (native asset feed) blocks the entire paymaster, not just one token — a broad, protocol-wide route failure reachable from an ordinary user transaction (submitting a UserOp), matching "a route unable to deliver messages" pattern of impact (here, unable to deliver gas sponsorship/service).

### Likelihood Explanation
Chainlink feed operators/multisigs can pause or effectively block a feed (as documented in the cited OpenZeppelin post referenced by the original report), and this is an externally-triggerable condition, not requiring any malicious action within Hyperbridge itself. Any legitimate user attempting to use the paymaster after such an event will trigger the revert deterministically since the oracle call is unconditional and unguarded.

### Recommendation
Wrap all `AggregatorV3Interface` calls (`latestRoundData()`, `decimals()`) in `try/catch` inside `_getOraclePrice`, and define an explicit fallback behavior on failure — e.g., reject that specific token/mode gracefully (allowing other tokens/native gas payment to continue) rather than reverting the entire pricing pipeline, and/or allow governance to pre-register a fallback oracle per token so a single feed outage does not take down sponsorship for all registered tokens.

### Proof of Concept
1. Governance registers `tokenA` with Chainlink oracle `O_native` (native/USD) and `O_tokenA` (tokenA/USD) via `_registerToken`, per `SimplexPaymaster.sol:392-404`.
2. Chainlink's aggregator multisig for `O_native` (or `O_tokenA`) pauses/deprecates the feed such that `latestRoundData()` reverts (a known, documented Chainlink capability).
3. Any user submits a UserOperation with `paymasterData` mode `0x00`/`0x02` naming `tokenA` (or any other registered token, since `nativeOracle` is always queried).
4. `EntryPoint` invokes `validatePaymasterUserOp` → `_validatePaymasterUserOp` → `_fetchDetails` → `_tokenPrice` → `_getOraclePrice(nativeOracle, ...)`.
5. The unguarded `oracle.latestRoundData()` call reverts, propagating up through `_fetchDetails` and causing `_validatePaymasterUserOp` to revert; the UserOperation is rejected by bundlers.
6. This applies to **every** UserOperation for **every** registered token until governance intervenes, since the native oracle is queried unconditionally on every call — a full DoS of the paymaster's gas-sponsorship service.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L524-546)
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
