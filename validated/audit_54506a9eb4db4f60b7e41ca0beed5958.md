### Title
SimplexPaymaster's Chainlink price fetch ignores min/max answer bounds, allowing token/gas mispricing when a feed is clamped - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster._getOraclePrice()` validates only that a Chainlink `latestRoundData()` answer is positive and not stale, but never checks the answer against the aggregator's configured `minAnswer`/`maxAnswer` circuit-breaker bounds. This mirrors the reported IronBank issue where `getPriceFromChainlink()` fails to detect a clamped price feed.

### Finding Description
`_getOraclePrice` in `evm/src/utils/SimplexPaymaster.sol` fetches `latestRoundData()` and only reverts on non-positive or stale answers: [1](#0-0) 

This price feed is used both to compute the gas-sponsorship price a UserOp sender pays in ERC-20 tokens (`_tokenPrice`) and to size the minimum swap output when recycling fees (`swapAndDeposit`): [2](#0-1) [3](#0-2) 

`SimplexPaymaster` is explicitly documented as a "fully onchain, permissionless ERC-4337 v0.8 paymaster that accepts ERC-20 stablecoins ... for gas payment," reachable by any UserOp sender through `_validatePaymasterUserOp`: [4](#0-3) [5](#0-4) 

If a registered token's Chainlink feed price craters far below its aggregator-configured `minAnswer` (analogous to the LUNA/UST crash cited in the report), `latestRoundData()` will continue reporting the floor price instead of the real, much lower price. `_getOraclePrice` accepts this clamped value uncritically because it is positive and fresh.

### Impact Explanation
Because `tokenUsd` feeds directly into the denominator of `_tokenPrice` (tokens required per unit of gas), an inflated `tokenUsd` (stuck at the floor while the real price has collapsed) causes the paymaster to under-price gas in terms of that token. An attacker can acquire the collapsed/near-worthless token cheaply on the open market, then use it via `_validatePaymasterUserOp`/PaymasterERC20 to pay for gas sponsorship computed against the stale, much-higher clamped Chainlink price — extracting real ETH-denominated gas value from the paymaster's EntryPoint deposit for a fraction of its true cost. Repeated at scale this drains the paymaster's EntryPoint stake/deposit, which is funded by governance/treasury, constituting a concrete theft-of-funds vector against protocol-controlled assets. The same stale-price input also corrupts `amountOutMin` in `swapAndDeposit`, exposing the fee-recycling swap to execution at deceptive prices.

### Likelihood Explanation
Any ERC-20 with a Chainlink feed configured with tight min/max bounds (common for stablecoins and many long-tail assets) can hit this condition during a severe depeg or crash, a scenario that has occurred historically (e.g., UST/LUNA, various stablecoin depegs). Governance registers arbitrary tokens with feeds via `_registerToken`, and exploitation requires no special privilege — merely submitting a UserOp using the affected token, which is exactly the permissionless flow this contract is designed to support.

### Recommendation
In `_getOraclePrice`, fetch the aggregator's `minAnswer`/`maxAnswer` (or equivalent bounds) and revert if `answer` is at or near those bounds, per Chainlink's documented guidance for handling min/max price limits. Alternatively, maintain a governance-configurable sanity band per token and reject prices outside it, and add a circuit breaker/pause path for a token whose oracle is flagged as saturated.

### Proof of Concept
1. Governance registers token `T` with Chainlink feed `F` via `_registerToken`, where `F` has `minAnswer = $0.01`.
2. Market price of `T` collapses to `$0.00001`; `F.latestRoundData()` continues returning `answer = minAnswer ($0.01)` since Chainlink clamps to the aggregator's floor.
3. Attacker buys a large quantity of `T` on the open market for negligible real cost (true price `$0.00001`).
4. Attacker submits UserOps using `SimplexPaymaster` with mode `0x00`/`0x02` paymasterData referencing `T`; `_tokenPrice`/`_getOraclePrice` price gas sponsorship using the stale `$0.01` valuation of `T` instead of its real `$0.00001` value.
5. Attacker's UserOps get sponsored (real ETH consumed from the paymaster's EntryPoint deposit) while only paying token amounts computed against the inflated, clamped price — extracting real value from the paymaster far in excess of the token's true worth, repeatable until the deposit/treasury is drained.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L53-58)
```text
/// @title  SimplexPaymaster
/// @author Polytope Labs
/// @notice Fully onchain, permissionless ERC-4337 v0.8 paymaster that accepts
///         ERC-20 stablecoins (USDC, USDT, or any token with a Chainlink feed)
///         for gas payment. Deployed behind an ERC1967Proxy and administered
///         exclusively through Hyperbridge governance.
```

**File:** evm/src/utils/SimplexPaymaster.sol (L464-467)
```text
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L492-510)
```text
    function _validatePaymasterUserOp(PackedUserOperation calldata userOp, bytes32 userOpHash, uint256 maxCost)
        internal
        override
        returns (bytes memory context, uint256 validationData)
    {
        uint256 postOpGasLimit = userOp.paymasterPostOpGasLimit();
        if (postOpGasLimit > MAX_POST_OP_GAS_LIMIT || postOpGasLimit < MIN_POST_OP_GAS_LIMIT) {
            revert InvalidPostOpGasLimit(postOpGasLimit, MIN_POST_OP_GAS_LIMIT, MAX_POST_OP_GAS_LIMIT);
        }

        bytes calldata data = userOp.paymasterData();
        if (data.length == 0) revert InvalidPaymasterData(0);
        if (uint8(data[0]) == 0x00) {
            if (data.length < 21) revert InvalidPaymasterData(data.length);
            address tokenAddr = address(bytes20(data[1:21]));
            TokenConfig memory cfg = tokenConfigs[tokenAddr];
            if (address(cfg.tokenOracle) == address(0)) revert TokenNotRegistered(tokenAddr);
            if (!cfg.active) revert TokenNotActive(tokenAddr);
            _executePermit(userOp);
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
