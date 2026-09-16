Confirmed: `_fetchDetails` calls `_tokenPrice(cfg)` which fetches both `nativeOracle` and `cfg.tokenOracle` prices through `_getOraclePrice`, and both are checked against the single, governance-configured `maxOracleAge` value shared across every oracle in the contract. [1](#0-0) 

### Title
Single `maxOracleAge` staleness bound applied across all Chainlink feeds with different real heartbeats causes stale-price acceptance or spurious paymaster DoS - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster` prices ERC-20 gas payments using two independent Chainlink feeds — `nativeOracle` and each token's `tokenOracle` — but validates both against one shared `maxOracleAge` value instead of a per-feed heartbeat. [2](#0-1)  This is the same "one interval for many feeds with different heartbeats" defect described in the reported Chainlink adaptor issue.

### Finding Description
`Params.maxOracleAge` and the corresponding storage variable `maxOracleAge` are a single, contract-wide bound documented as needing to cover heartbeats "BSC stablecoins ~27s, Base/Ethereum stablecoins up to 24h" — i.e., the developers already acknowledge wildly different real heartbeats exist across the native/USD and token/USD feeds this contract prices. [3](#0-2)  `_getOraclePrice` is called once for `nativeOracle` and once for `cfg.tokenOracle` inside `_tokenPrice`, and both calls use the exact same `maxOracleAge` threshold to decide staleness: `if (block.timestamp - updatedAt > maxOracleAge) revert StaleOraclePrice(...)`. [4](#0-3)  `_tokenPrice` is reached from `_fetchDetails`, which every ERC-4337 `UserOperation` using this paymaster invokes during `PaymasterERC20`'s pricing hook. [5](#0-4) 

Since governance can only configure one `maxOracleAge` for the whole paymaster (bounded by `MAX_ORACLE_AGE = 7 days`), whichever value is chosen is wrong for at least one of the two feeds actually used to price any given token:
- If `maxOracleAge` is set loose enough to tolerate the slower feed's real heartbeat (e.g., a stablecoin feed with a 24h heartbeat), a fast-heartbeat feed (e.g., a native asset feed with a much shorter heartbeat) can go stale for a long time without tripping `StaleOraclePrice`, silently pricing gas off a materially outdated Chainlink answer.
- If `maxOracleAge` is set tight enough to catch staleness on the fast-heartbeat feed, the slow-heartbeat feed will legitimately fail to update within that window under normal operation, causing `_getOraclePrice` to revert with `StaleOraclePrice` even though the feed is behaving exactly as Chainlink intends — bricking every `UserOperation` priced through that token until governance manually widens the bound.

The same shared value is also used in `swapAndDeposit`'s fee-recycling swap pricing. [6](#0-5) 

### Impact Explanation
Because `nativeOracle` and every registered `tokenOracle` are configured independently but validated against one age bound, the paymaster either (a) accepts stale price data for the faster-heartbeat feed, letting a solver's `UserOperation` be charged an ERC-20 amount computed from an outdated price relative to the live gas cost, or (b) unpredictably reverts `fetchDetails`/`_validatePaymasterUserOp` for any token whose feed's normal heartbeat exceeds the tightened bound, denying gas sponsorship for every UserOperation using that token — a DoS on the permissionless paymaster path reachable by any unprivileged solver submitting a UserOperation.

### Likelihood Explanation
This is a configuration-shape defect, not exploit-of-attacker-input: it manifests deterministically whenever governance sets a single `maxOracleAge` for a native/token oracle pair whose real Chainlink heartbeats diverge (a documented, common situation per the contract's own comments), and it will recur every time a new token with a different-heartbeat oracle is registered via `RegisterToken`. [7](#0-6) 

### Recommendation
Store a per-oracle staleness bound (e.g., in `TokenConfig` and alongside `nativeOracle`) instead of one global `maxOracleAge`, so each feed is checked against its own real Chainlink heartbeat plus a safety margin, matching the recommendation in the referenced report to use different `heartbeatInterval` values per token/feed.

### Proof of Concept
1. Governance registers `tokenOracle` for USDC (24h heartbeat) and sets `nativeOracle` to an ETH/USD feed with, say, a 1h heartbeat, choosing `maxOracleAge = 90000` (25h) to accommodate USDC's heartbeat, per the deploy script default. [8](#0-7) 
2. The ETH/USD feed stops updating for >1h but <25h — well past its own real heartbeat, so its `updatedAt` is legitimately "very stale" for that feed, yet `_getOraclePrice` still accepts it because `block.timestamp - updatedAt <= maxOracleAge`. [9](#0-8) 
3. Any solver submits a `UserOperation` using this paymaster; `_fetchDetails` computes `tokenPrice` from the stale ETH/USD answer via `_tokenPrice`, mispricing the ERC-20 amount charged relative to actual gas cost. [10](#0-9) 
4. Conversely, if governance instead tightens `maxOracleAge` to 1h to protect the native feed, every USDC-paying UserOperation begins reverting with `StaleOraclePrice` as soon as the USDC feed goes past 1h without an update — which is normal behavior for a 24h-heartbeat feed — denying gas sponsorship contract-wide for that token, as exercised by `testStaleOracleReverts`/`testUpdateParamsTightensOracleAge`. [11](#0-10)

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L124-125)
```text
        /// @dev Registers or updates a supported ERC-20 token and its token/USD feed.
        RegisterToken,
```

**File:** evm/src/utils/SimplexPaymaster.sol (L146-148)
```text
        /// @notice Maximum oracle staleness. Chainlink heartbeats vary per chain
        ///         (BSC stablecoins ~27s, Base/Ethereum stablecoins up to 24h).
        uint256 maxOracleAge;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L196-199)
```text
    AggregatorV3Interface public nativeOracle;
    uint8 public nativeOracleDecimals;
    uint256 public maxOracleAge;
    uint256 public markupBps;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L454-466)
```text
    function swapAndDeposit(address token, uint256 amountIn) external {
        if (msg.sender != treasury) revert UnauthorizedCall();
        address router = IDispatcher(host()).uniswapV2Router();
        if (router == address(0)) revert InvalidRouter(router);
        TokenConfig memory cfg = tokenConfigs[token];
        if (address(cfg.tokenOracle) == address(0)) revert TokenNotRegistered(token);

        uint256 balance = IERC20(token).balanceOf(address(this));
        if (amountIn == 0 || amountIn > balance) amountIn = balance;

        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
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
