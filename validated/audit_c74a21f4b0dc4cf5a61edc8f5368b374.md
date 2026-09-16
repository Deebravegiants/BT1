I have sufficient evidence to render a final determination.

### Title
Missing Chainlink round-completeness check in `SimplexPaymaster._getOraclePrice` can charge users a stale gas price - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster._getOraclePrice` consumes `AggregatorV3Interface.latestRoundData()` and validates that the answer is positive and not older than `maxOracleAge`, but never checks round completeness (`answeredInRound >= roundId`), matching the exact gap identified in the external Chainlink report.

### Finding Description
`_getOraclePrice` destructures `latestRoundData()` and only checks the price sign and staleness of `updatedAt`: [1](#0-0) 

The `roundId` and `answeredInRound` return values are discarded entirely, so there is no check equivalent to `require(roundId <= answeredInRound)`. This is the exact bug class from the external report: `latestRoundData()` can return data from a round that has not been fully carried over, and the `updatedAt` timestamp alone does not guarantee the returned answer reflects the round the aggregator is currently transitioning through (e.g., when the underlying feed/aggregator is mid-migration or when a sub-aggregator behind the proxy has stalled while the proxy's timestamp still looks "fresh enough" relative to `maxOracleAge`). This price feeds directly into `_tokenPrice`, which every unprivileged UserOp sender using this paymaster's Permit or Permit2 payment modes triggers on each `_fetchDetails`/`_prefund` call: [2](#0-1) [3](#0-2) 

It also drives the treasury-permissioned `swapAndDeposit` minimum-output calculation: [4](#0-3) 

### Impact Explanation
An incomplete/misreported round can cause `_getOraclePrice` to return a stale price that nonetheless satisfies the `maxOracleAge` staleness check (because the proxy's `updatedAt` can lag round completion without exceeding the staleness window). Since `tokenPrice` directly sets how much ERC-20 is pulled from a UserOp sender relative to native gas cost, an incompletely-updated Chainlink answer can cause the paymaster to over-charge or under-charge every unprivileged UserOp sender that pays gas through this paymaster, i.e., concrete loss of funds either to users (overcharge) or to the paymaster's treasury (undercharge, draining subsidized gas). This satisfies the Medium bar of "concrete theft ... of funds" reachable from an ordinary, permissionless user action (submitting a UserOp).

### Likelihood Explanation
The contract's authors were clearly aware of Chainlink oracle risk — they already added `StaleOraclePrice` and `InvalidOraclePrice` checks and tests for both — which shows this is a hardening path they intended to close, yet the round-completeness check was omitted. The condition triggers whenever a configured Chainlink feed (native or any registered token) experiences a round in transition; this is a documented, real-world Chainlink occurrence (not attacker-induced), making it a plausible, low-effort-to-trigger scenario compared to most oracle manipulation bugs, though it depends on the specific feed's operational behavior, which somewhat reduces frequency.

### Recommendation
Add the round-completeness check alongside the existing checks in `_getOraclePrice`:
```solidity
(uint80 roundId, int256 answer,, uint256 updatedAt, uint80 answeredInRound) = oracle.latestRoundData();
if (answer <= 0) revert InvalidOraclePrice(address(oracle), answer);
if (answeredInRound < roundId) revert IncompleteRound(address(oracle), roundId, answeredInRound);
if (block.timestamp - updatedAt > maxOracleAge) revert StaleOraclePrice(address(oracle), updatedAt);
```

### Proof of Concept
1. A Chainlink price feed registered as `nativeOracle` or a `tokenConfigs[token].tokenOracle` enters a state where `latestRoundData()` returns `answeredInRound < roundId` (an in-progress round) while `updatedAt` is still within `maxOracleAge`.
2. Any unprivileged UserOp sender submits a UserOp using mode `0x00` (Permit) or `0x02` (Permit2); `_fetchDetails` calls `_tokenPrice(cfg)` → `_getOraclePrice`, which passes both the positivity and staleness checks despite the round being incomplete.
3. The resulting `tokenPrice` is used in `_prefund`/`PaymasterERC20._erc20Cost` to pull ERC-20 tokens from the sender via `transferFrom`/Permit2, charging an amount derived from the stale/incomplete round data rather than the true current price, transferring value between the user and the paymaster's treasury based on incorrect pricing.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L461-467)
```text
        uint256 balance = IERC20(token).balanceOf(address(this));
        if (amountIn == 0 || amountIn > balance) amountIn = balance;

        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;
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
