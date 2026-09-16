Confirmed: `_fetchDetails` (called for every UserOperation submitted through the paymaster) computes `tokenPrice` via `_tokenPrice`, which calls `_getOraclePrice` twice.I have sufficient evidence to conclude the analysis.

### Title
Chainlink Oracle Circuit-Breaker (`minAnswer`/`maxAnswer`) Not Checked in `SimplexPaymaster._getOraclePrice` - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster._getOraclePrice` fetches Chainlink data via `latestRoundData()` and validates only that the answer is positive and not stale [1](#0-0) . It never checks the returned `answer` against the underlying aggregator's `minAnswer`/`maxAnswer` bounds. Every ERC‑4337 `UserOperation` that pays gas through this paymaster is priced using this function via `_fetchDetails` → `_tokenPrice` → `_getOraclePrice`, so any unprivileged bandwidth purchaser (a UserOperation sender selecting a registered token) is exposed to whatever stale/clamped price the feed reports during a crash.

### Finding Description
`_getOraclePrice` is the sole price source for both the sponsored token and the native asset used in `_tokenPrice`, which is invoked from the reachable, permissionless entry point `_fetchDetails`, called for every submitted UserOperation [2](#0-1) . The same unbounded price is also used in the treasury-only `swapAndDeposit`, but the primary unprivileged attack surface is `_fetchDetails`/`_prefund`, reachable by any UserOperation sender specifying a registered ERC-20 as the gas token [3](#0-2) .

`_getOraclePrice` only guards against non-positive answers and staleness beyond `maxOracleAge`; it performs no comparison of `answer` against the aggregator's `minAnswer`/`maxAnswer` circuit-breaker bounds: [4](#0-3) 

Chainlink aggregators clamp reported prices to `[minAnswer, maxAnswer]`; when the true market price of the sponsored token falls below `minAnswer` (a crash scenario), `latestRoundData()` keeps returning `minAnswer` — a value strictly higher than the token's real worth — without reverting and without the staleness check catching it (the round can keep updating with the clamped price).

### Impact Explanation
Because `tokenPrice = (nativeUsd * 10^tokenDecimals) / tokenUsd` is monotonically decreasing in `tokenUsd`, an inflated `tokenUsd` (stuck at `minAnswer` during a crash) understates the amount of the crashed token a UserOperation sender must pay for real native gas that the paymaster fronts via the EntryPoint deposit [5](#0-4) . An attacker holding a token that has crashed far below the feed's `minAnswer` floor can pay for gas at a materially better-than-market rate, draining real native value (ETH/BNB) from the paymaster's EntryPoint deposit/treasury in exchange for a near-worthless token — the same fund-drain mechanism described in the referenced report, adapted to a paymaster gas-market rather than a lending market.

### Likelihood Explanation
Every registered token is a candidate; the paymaster explicitly documents it accepts "any token with a Chainlink feed" [6](#0-5) . Any listed token undergoing a sharp de-pegging/crash event (a realistic, externally-triggered market condition, not requiring privileged access) that pushes its price below the feed's configured `minAnswer` immediately opens this window; the attacker only needs to submit a normal UserOperation with mode 0x00/0x02 paymasterData naming that token, which is fully unprivileged.

### Recommendation
In `_getOraclePrice`, fetch and cache each aggregator's `minAnswer`/`maxAnswer` (or query them from the underlying `AggregatorV2V3Interface`/proxy `aggregator()`), and revert with `InvalidOraclePrice` when `answer <= minAnswer || answer >= maxAnswer`, mirroring the staleness/non-positivity checks already present.

### Proof of Concept
1. Token `T` is registered with oracle `O` whose underlying aggregator has `minAnswer = $0.10`.
2. `T`'s real market price collapses to $0.001 (e.g., depeg/exploit). `O.latestRoundData()` continues returning `answer = $0.10` (clamped), with `updatedAt` refreshed each round so the staleness check in `_getOraclePrice` passes.
3. Attacker (who acquired large amounts of near-worthless `T` cheaply) submits a UserOperation with `paymasterData` mode 0x00 naming `T` as the gas token.
4. `_fetchDetails` computes `tokenPrice` using the clamped $0.10 valuation via `_tokenPrice`/`_getOraclePrice` [7](#0-6) , so the attacker pays only `weiCost * tokenPrice` in `T`, valued at 100x its real market price.
5. The paymaster's real native balance (from EntryPoint deposit/treasury) is spent sponsoring the op while receiving `T` worth a fraction of the actual gas cost — repeatable across many UserOperations until the treasury is drained or the token is deactivated by governance.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L55-57)
```text
/// @notice Fully onchain, permissionless ERC-4337 v0.8 paymaster that accepts
///         ERC-20 stablecoins (USDC, USDT, or any token with a Chainlink feed)
///         for gas payment. Deployed behind an ERC1967Proxy and administered
```

**File:** evm/src/utils/SimplexPaymaster.sol (L516-523)
```text
    /// @dev Returns the token to charge and its price relative to native gas.
    ///
    ///      PaymasterERC20 computes `erc20Cost = weiCost * tokenPrice / 1e18`,
    ///      so tokenPrice must be token base units per wei, scaled by 1e18:
    ///        tokenPrice = (nativeUsd * 10^tokenDecimals) / tokenUsd
    ///      e.g. BNB at $600, USDC at $1 with 6 decimals: 0.001 BNB (1e15 wei)
    ///      should cost 0.60 USDC (600000 units), giving tokenPrice = 6e8, which
    ///      is exactly (600e8 * 1e6) / 1e8. Markup is applied on top.
```

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
