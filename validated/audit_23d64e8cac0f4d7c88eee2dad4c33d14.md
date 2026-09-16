## Title
Chainlink circuit breaker (min/maxAnswer) not enforced in `SimplexPaymaster` oracle pricing, enabling underpriced gas sponsorship during a stablecoin depeg - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster` prices ERC-20 gas payments using two Chainlink feeds (native/USD and token/USD) read through `_getOraclePrice`, but it only validates that the returned `answer` is positive and not stale — it never checks the answer against the underlying aggregator's `minAnswer`/`maxAnswer` circuit-breaker bounds, exactly the bug class described in the external report.

### Finding Description
`_getOraclePrice` fetches `latestRoundData()` from a Chainlink `AggregatorV3Interface` and only guards against non-positive and stale answers: [1](#0-0) 

This value directly feeds `_tokenPrice`, which computes the ERC-20 gas price a UserOperation sender must pay: [2](#0-1) 

`_tokenPrice` is invoked from `_fetchDetails`, which is called during `_validatePaymasterUserOp`/`_prefund` for every permissionless ERC-4337 `UserOperation` that uses this paymaster — i.e., any unprivileged sender/bundler submitting a UserOp reaches this pricing path with no privileged gate: [3](#0-2) 

Chainlink aggregators (per the report) apply a hard-coded `minAnswer`/`maxAnswer` circuit breaker: if the real market price moves outside these bounds, `latestRoundData()` keeps returning the capped bound instead of the true price, while still reporting a fresh `updatedAt` and a positive value — so neither of `_getOraclePrice`'s checks catches it. If a supported stablecoin registered as `tokenOracle` (e.g., a BSC/Base stablecoin per the contract's own doc comments) depegs sharply downward past its feed's `minAnswer`, the aggregator continues reporting the higher, capped `minAnswer` instead of the token's true collapsed price. Since `tokenPrice = nativeUsd * 10^tokenDecimals / tokenUsd`, an artificially inflated `tokenUsd` makes `tokenPrice` (i.e., the amount of that depegged token charged per unit of gas) understated, letting UserOperation senders pay near-worthless depegged tokens for real native-asset gas sponsorship.

### Impact Explanation
The paymaster fronts real native currency (from its EntryPoint deposit, funded by governance/treasury) for every sponsored UserOperation and is repaid only in the mispriced ERC-20 token. During a stablecoin depeg exceeding the feed's circuit-breaker bound, an attacker can mass-submit UserOperations paying with the depegged (near-worthless) token while the contract still values it near its peg, draining the paymaster's EntryPoint deposit/native reserves for a fraction of their real cost. This is a High-impact fund-drain vector on protocol-owned assets (the paymaster's gas reserve and treasury-fed deposit), reachable purely by unprivileged UserOperation submission with no governance/admin involvement.

### Likelihood Explanation
Likelihood is Low, matching the referenced report: it requires an underlying asset to actually break through its Chainlink feed's configured `minAnswer`/`maxAnswer` bound (a rare market event), but this has previously occurred for real assets (e.g., LUNA/UST), and the report explicitly notes several Arbitrum feeds (ETH/USD, major stablecoins) still enforce these bounds today, so it is not a purely theoretical scenario for stablecoins the paymaster is designed to support.

### Recommendation
In `_getOraclePrice` (`evm/src/utils/SimplexPaymaster.sol`), fetch each configured aggregator's `minAnswer`/`maxAnswer` (via `AggregatorV2V3Interface`/`aggregator()`) once at registration time (store alongside `TokenConfig`/`nativeOracle` config) and validate on every read that `answer` is strictly inside `(minAnswer, maxAnswer)`, reverting (e.g., with a new `InvalidOraclePrice`/circuit-breaker error) rather than silently accepting a capped value, mirroring the diff suggested in the report.

### Proof of Concept
1. Governance registers a stablecoin `token` via `RegisterToken` with a Chainlink `tokenOracle` whose aggregator enforces `minAnswer = 0.99e8` (typical for some deployed feeds).
2. The stablecoin depegs to $0.10 due to a real-world event; the aggregator's on-chain circuit breaker caps `latestRoundData().answer` at `minAnswer = 0.99e8`, with `updatedAt` continuously refreshed (within `maxOracleAge`).
3. `_getOraclePrice` returns `0.99e8` for `tokenUsd`, passing both its `answer <= 0` and staleness checks (`evm/src/utils/SimplexPaymaster.sol` lines 662-668).
4. `_tokenPrice` computes `tokenPrice = nativeUsd * 10^tokenDecimals / tokenUsd` using the inflated `tokenUsd`, understating the true cost of gas in the depegged token by ~10x.
5. An attacker submits UserOperations sponsored by `SimplexPaymaster` using mode 0x00/0x02, paying in the depegged token at the stale capped rate, draining the paymaster's EntryPoint-deposited native balance for a fraction of its real value.

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
