### Title
Chainlink oracle prices used in `SimplexPaymaster._getOraclePrice` can be stale/carried-over from a previous round, letting a UserOp sender under- or over-pay for gas - (`evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster` prices ERC-20 gas payments against Chainlink `AggregatorV3Interface.latestRoundData()` feeds. The staleness check only compares `block.timestamp - updatedAt` against `maxOracleAge`; it never checks that the round actually advanced (`roundId`/`answeredInRound` consistency), so a feed that carries over a previous round's answer while still refreshing `updatedAt` (or otherwise reports a non-fresh answer without failing the naive timestamp check) will be silently accepted as the current price.

### Finding Description
`_getOraclePrice` fetches `latestRoundData()` and validates only two conditions: [1](#0-0) 

```solidity
function _getOraclePrice(AggregatorV3Interface oracle, uint8 oracleDecimals) internal view returns (uint256) {
    (, int256 answer,, uint256 updatedAt,) = oracle.latestRoundData();

    if (answer <= 0) revert InvalidOraclePrice(address(oracle), answer);
    if (block.timestamp - updatedAt > maxOracleAge) {
        revert StaleOraclePrice(address(oracle), updatedAt);
    }
    ...
}
```

This is the same pattern flagged in the external report for `LibUbiquityPool.updateChainLinkCollateralPrice`: it discards `roundId` and `answeredInRound` entirely, so there is no way to detect a round whose answer was carried over from an earlier round while `updatedAt` still advances (a known Chainlink aggregator/proxy behavior), nor any way to detect a round that started but never completed. Any manipulated, degraded, or misbehaving feed that satisfies "not too old" while returning a non-current answer passes validation.

This price feeds directly into the amount an unprivileged UserOperation sender is charged for gas: [2](#0-1) 

```solidity
function _tokenPrice(TokenConfig memory cfg) internal view returns (uint256) {
    uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
    uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);

    return (nativeUsd * (10 ** cfg.tokenDecimals) * (10_000 + markupBps)) / (tokenUsd * 10_000);
}
```

`_tokenPrice`/`_getOraclePrice` are invoked from `_fetchDetails`, which is reached during `_validatePaymasterUserOp` for every UserOperation submitted by any address (an unprivileged "bandwidth purchaser" paying gas via an ERC-20): [3](#0-2) 

```solidity
function _fetchDetails(
    PackedUserOperation calldata userOp,
    bytes32 /* userOpHash */
)
    internal
    view
    override
    returns (uint256 validationData, IERC20 token, uint256 tokenPrice)
{
    ...
    tokenPrice = _tokenPrice(cfg);
    token = IERC20(tokenAddr);
    ...
}
```

The same tainted price also sizes the minimum output of the treasury-triggered `swapAndDeposit` fee-recycling swap, compounding the impact if a stale/carried-over price understates the token's true USD value.

### Impact Explanation
`PaymasterERC20` (the inherited base) computes `erc20Cost = weiCost * tokenPrice / 1e18` and pulls that amount from the UserOp sender while the paymaster's own EntryPoint deposit fronts the real ETH gas cost. If the Chainlink feed reports a carried-over/stale-but-fresh-looking answer that understates the native asset's USD price (or overstates the ERC-20 token's USD price), `tokenPrice` is computed too low: any unprivileged UserOp sender can have their gas sponsored while paying materially less than the paymaster's real ETH outlay, draining the paymaster's EntryPoint deposit over repeated operations — a concrete theft-of-funds vector reachable from ordinary UserOperation submission, matching the Medium-severity impact described in the source report (users extracting more value than they should from a system relying on unchecked Chainlink data).

### Likelihood Explanation
Likelihood is bounded by how often a given Chainlink aggregator serves a stale/carried-over round while its `updatedAt` still passes the naive age check; this is a documented Chainlink behavior (heartbeat-only updates, deviation-threshold feeds, or feed operator issues) rather than a hypothetical. The check runs on every UserOp validation, so it applies to the entire live surface of the paymaster, not a rare code path, and requires no privileged action from the attacker — only submitting a UserOperation.

### Recommendation
In `_getOraclePrice`, retrieve `roundId` and `answeredInRound` from `latestRoundData()` and validate that the round actually completed and matches the fetched round, e.g. `require(answeredInRound == roundId, "stale round")`, in addition to the existing `answer > 0` and staleness checks. Consider also reverting when `startedAt == 0` (round never started).

### Proof of Concept
1. Governance registers a Chainlink feed for `nativeOracle` (or a token oracle) via `RegisterToken`/`UpdateParams`.
2. The feed's underlying aggregator enters a state where `latestRoundData()` returns a `roundId` whose `answeredInRound` does not match (a carried-over/incomplete round), while `updatedAt` is recent enough to pass `block.timestamp - updatedAt <= maxOracleAge`.
3. Any address submits a UserOperation using `SimplexPaymaster` for ERC-20 gas payment; `_validatePaymasterUserOp` → `_fetchDetails` → `_tokenPrice` → `_getOraclePrice` (evm/src/utils/SimplexPaymaster.sol:662-676) accepts the stale answer because only `answer > 0` and the timestamp delta are checked.
4. The computed `tokenPrice` is below the true exchange rate, so the sender's `erc20Cost` charge understates the ETH the paymaster fronts via the EntryPoint, letting the sender extract value from the paymaster's deposit on every such UserOp.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L524-547)
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
