### Title
Missing Chainlink circuit-breaker (min/max answer) validation in `SimplexPaymaster._getOraclePrice()` allows mispriced gas payments during extreme price moves - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster._getOraclePrice()` validates that a Chainlink `latestRoundData()` answer is positive and not stale, but never checks the answer against the aggregator's `minAnswer`/`maxAnswer` circuit-breaker bounds [1](#0-0) . If the underlying asset's market price crashes below (or spikes above) the aggregator's configured bounds, Chainlink will keep returning the pinned min/max value rather than the true price, and this function will accept it as valid since it is still positive and fresh.

### Finding Description
`_getOraclePrice()` is used for both the token/USD and native/USD legs of gas-fee pricing:
- `_tokenPrice()` calls it for `nativeOracle` and each token's `tokenOracle` to compute `tokenPrice` [2](#0-1) .
- `_fetchDetails()`, called on every `validatePaymasterUserOp`, uses `_tokenPrice(cfg)` to determine how much of the sponsored ERC-20 to charge for gas [3](#0-2) .
- `swapAndDeposit()` also uses `_getOraclePrice` for both legs to compute the minimum acceptable swap output when recycling collected fees [4](#0-3) .

The only checks performed are:
```solidity
if (answer <= 0) revert InvalidOraclePrice(address(oracle), answer);
if (block.timestamp - updatedAt > maxOracleAge) revert StaleOraclePrice(...);
```
There is no comparison of `answer` against the aggregator's `minAnswer`/`maxAnswer` circuit-breaker range. As documented in the original Chainlink audit finding this report is based on, when an underlying asset experiences an extreme depeg/crash (or spike) beyond the aggregator's configured bounds, the aggregator continues to report the pinned boundary value as a valid, fresh, positive answer — it does not revert or flag staleness. `_getOraclePrice()` therefore accepts and normalizes this stale/incorrect boundary price as if it were the live market price.

`SimplexPaymaster` is a fully permissionless ERC-4337 paymaster: any UserOp sender can trigger `_validatePaymasterUserOp` → `_fetchDetails` → `_tokenPrice` → `_getOraclePrice` simply by submitting a UserOp with paymasterData naming a registered stablecoin [5](#0-4) . No governance or relayer authorization is required for this path — governance/relayer gating only protects `onAccept` administrative actions [6](#0-5) .

### Impact Explanation
If the native-asset oracle or a registered token oracle hits its circuit breaker during a severe market dislocation (e.g., a stablecoin depeg or a chain's native asset crashing), `tokenPrice` computed by `_tokenPrice()` will be based on the pinned min/max boundary price instead of the real price. Since `tokenPrice = (nativeUsd * 10^tokenDecimals * (10000+markupBps)) / (tokenUsd * 10000)`, a wrong `nativeUsd` or `tokenUsd` directly under- or over-charges every UserOp sender for the gas the paymaster fronts:
- If the pinned price understates the true cost of native gas relative to the stablecoin, users are undercharged, allowing the paymaster's treasury/deposit to be drained of value relative to the gas actually spent (loss of protocol funds).
- If it overstates it, users are systematically overcharged (loss of funds to users), and the same broken price feeds `swapAndDeposit`'s `amountOutMin`, which could also let a manipulated/pinned price be used to justify an unfavorable swap.

This constitutes a concrete funds-loss vector against a permissionless, unprivileged entry point (any UserOp sender / solver paying gas through Simplex), consistent with a Medium-severity oracle-mispricing issue.

### Likelihood Explanation
Triggering requires an external market event (an extreme price crash/spike hitting Chainlink's configured min/max bounds) rather than any special privilege — any address that can submit a UserOp against a Simplex-sponsored token benefits from or is harmed by the resulting mispricing, so exploitation/exposure is not gated behind admin or relayer permissions. Such circuit-breaker events are rare but have occurred historically (e.g., LUNA/UST depegs) for exactly the asset classes (stablecoins, native gas assets) this paymaster prices.

### Recommendation
In `_getOraclePrice()`, fetch and cache each aggregator's `minAnswer`/`maxAnswer` (via `AggregatorV2V3Interface` or the underlying `aggregator()`), and revert if the returned `answer` is at or outside those bounds, mirroring the staleness/positivity checks already present:
```solidity
function _getOraclePrice(AggregatorV3Interface oracle, uint8 oracleDecimals) internal view returns (uint256) {
    (, int256 answer,, uint256 updatedAt,) = oracle.latestRoundData();
    if (answer <= 0) revert InvalidOraclePrice(address(oracle), answer);
    if (answer <= minAnswer[oracle] || answer >= maxAnswer[oracle]) revert InvalidOraclePrice(address(oracle), answer);
    if (block.timestamp - updatedAt > maxOracleAge) revert StaleOraclePrice(address(oracle), updatedAt);
    ...
}
```
Store the bounds per registered oracle at `RegisterToken`/`UpdateParams` governance time, or query the aggregator's proxy `aggregator()` and its `minAnswer()`/`maxAnswer()` at call time if supported on the target chain's feed implementation.

### Proof of Concept
1. Governance registers a token whose price is fed by a Chainlink aggregator with `minAnswer = X`.
2. The underlying asset's real market price crashes far below `X` (e.g., a stablecoin depeg to $0.10 while `minAnswer` is pinned at $0.90).
3. `oracle.latestRoundData()` returns `answer = X` (still positive, still fresh/updated), which `_getOraclePrice()` accepts as valid.
4. Any UserOp sender calls `validatePaymasterUserOp` with paymasterData mode `0x00`/`0x02` for that token; `_fetchDetails` → `_tokenPrice` computes `tokenPrice` using the stale pinned price `X` instead of the real $0.10, causing the sender to be undercharged (or overcharged, depending on direction) relative to the true value of gas being fronted by the paymaster, directly costing the paymaster's treasury. [7](#0-6)

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L95-105)
```text
///      Governance deliveries are further restricted to one relayer. The host
///      hands onAccept the handler's msg.sender as `incoming.relayer`; once
///      `_relayer` is set, any other submitter is refused before the body is
///      read, so a forged consensus proof alone cannot reach this contract.
///      The host records the refusal as undelivered and the authorised relayer
///      can resubmit. While `_relayer` is unset (a proxy upgraded without
///      {migrate}) every relayer passes, as on the gateway; governance can
///      never set it to zero afterwards. The relayer must be a plain EOA, not
///      an account that executes third-party calldata. Losing that key loses
///      governance over the deposit, stake and surplus for good: there is no
///      second key.
```

**File:** evm/src/utils/SimplexPaymaster.sol (L464-467)
```text
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L492-514)
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
        }

        return super._validatePaymasterUserOp(userOp, userOpHash, maxCost);
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L516-546)
```text
    /// @dev Returns the token to charge and its price relative to native gas.
    ///
    ///      PaymasterERC20 computes `erc20Cost = weiCost * tokenPrice / 1e18`,
    ///      so tokenPrice must be token base units per wei, scaled by 1e18:
    ///        tokenPrice = (nativeUsd * 10^tokenDecimals) / tokenUsd
    ///      e.g. BNB at $600, USDC at $1 with 6 decimals: 0.001 BNB (1e15 wei)
    ///      should cost 0.60 USDC (600000 units), giving tokenPrice = 6e8, which
    ///      is exactly (600e8 * 1e6) / 1e8. Markup is applied on top.
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
