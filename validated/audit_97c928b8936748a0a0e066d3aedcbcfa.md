## Title
Missing Chainlink round-completeness checks in `SimplexPaymaster._getOraclePrice()` can misprice gas fees paid by unprivileged UserOp senders - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster._getOraclePrice()` fetches Chainlink prices via `latestRoundData()` and only validates that the answer is positive and that `updatedAt` is not older than `maxOracleAge`. It never checks `answeredInRound >= roundId` or that `roundId != 0`, so it cannot detect a Chainlink round that reports a fresh-looking `updatedAt` timestamp while carrying a carried-over/incomplete answer from a prior round. [1](#0-0) 

### Finding Description
`_getOraclePrice` destructures `latestRoundData()` and discards `roundId` and `answeredInRound` entirely: [2](#0-1) 

Per Chainlink's documented caveats, `answeredInRound < roundId` (or `roundId == 0`) signals that the aggregator is returning a value carried over from a previous round rather than a freshly answered one for the current round — the exact condition this contract never checks. This is the identical root cause described in the external report for FlatMoney's `OracleModule._getOnchainPrice()`.

This function is directly reachable from any unprivileged UserOp sender (a "bandwidth purchaser" paying gas fees in an ERC-20 via the paymaster), not just governance:
- `_fetchDetails`, called on every UserOp during `validatePaymasterUserOp`, calls `_tokenPrice(cfg)` → `_getOraclePrice` for both the native and token oracle to compute `tokenPrice`. [3](#0-2) [4](#0-3) 
- That `tokenPrice` is then used by `_prefund`/`_erc20Cost` to compute how much ERC-20 token is pulled from the user (via Permit2 or `transferFrom`) to cover the UserOp's gas cost. [5](#0-4) 

Since any address can submit a UserOp using the paymaster's mode 0x00/0x02 paymasterData, any external actor can trigger `_getOraclePrice` and have the (potentially incomplete-round) price applied to the token amount charged, with no way for the contract to reject the bad round.

### Impact Explanation
If the Chainlink aggregator ever returns a completed-looking but stale/incomplete round (an anomaly the timestamp-only check cannot catch), `_getOraclePrice` will silently accept it and feed it into `tokenPrice`. Because `tokenPrice` directly determines the ERC-20 amount pulled from the UserOp sender (and the `expectedWei`/`amountOutMin` bound in `swapAndDeposit`), a stale/incorrect round can cause:
- Undercharging: users pay far less token than the true gas cost, draining paymaster's ERC-20 reserves/treasury value over time (an unbacked-mint-style theft against the paymaster).
- Overcharging: users' Permit2/transferFrom prefund is inflated, directly stealing user funds since the amount is deducted immediately in `_prefund`.

Both are concrete fund-theft outcomes reachable from a single unprivileged UserOp submission, matching Medium severity for this bug class.

### Likelihood Explanation
Exploitation requires Chainlink to actually surface an incomplete/stale round (a known, documented Chainlink edge case, not attacker-controlled) — this is an external-oracle precondition rather than something an attacker can force at will, which bounds likelihood. However, once such a round occurs, *any* unprivileged party can immediately submit a UserOp (no permission needed) and have the mispriced value applied, so there is no additional barrier on the Hyperbridge/paymaster side once the precondition is met.

### Recommendation
Mirror the referenced fix: destructure `roundId` and `answeredInRound` from `latestRoundData()` in `_getOraclePrice` and revert (e.g. with the existing `StaleOraclePrice`/`InvalidOraclePrice` errors or a new dedicated error) when `roundId == 0` or `answeredInRound < roundId`, in addition to the existing `updatedAt` staleness and positive-answer checks.

```solidity
function _getOraclePrice(AggregatorV3Interface oracle, uint8 oracleDecimals) internal view returns (uint256) {
    (uint80 roundId, int256 answer, , uint256 updatedAt, uint80 answeredInRound) = oracle.latestRoundData();

    if (roundId == 0 || answeredInRound < roundId) revert InvalidOraclePrice(address(oracle), answer);
    if (answer <= 0) revert InvalidOraclePrice(address(oracle), answer);
    if (block.timestamp - updatedAt > maxOracleAge) {
        revert StaleOraclePrice(address(oracle), updatedAt);
    }
    ...
}
```

### Proof of Concept
1. A Chainlink aggregator used as `nativeOracle` or a token's `tokenOracle` enters a state where `latestRoundData()` returns `updatedAt` within `maxOracleAge`, but `answeredInRound < roundId` (round not fully answered / carried-over answer) — a scenario Chainlink itself documents as possible.
2. Any user submits a UserOp using `paymasterData` mode `0x00` or `0x02` naming a registered token.
3. `_fetchDetails` → `_tokenPrice` → `_getOraclePrice` is invoked for both `nativeOracle` and the token oracle; neither call checks `roundId`/`answeredInRound`, so the incomplete-round answer passes through unchallenged.
4. The resulting `tokenPrice` is used in `_prefund`/`_erc20Cost` to pull ERC-20 tokens from the UserOp sender via Permit2 or `transferFrom`, at a price that does not reflect a genuinely completed oracle round, over- or under-charging the sender relative to the correct market price.

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
