### Title
Chainlink oracle circuit-breaker (`minAnswer`/`maxAnswer`) not checked in `SimplexPaymaster`, allowing mispriced gas payments - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster` prices ERC-20 gas payments purely from Chainlink `latestRoundData()`, validating only staleness and a positive answer. It never checks whether the returned answer sits at the underlying aggregator's `minAnswer`/`maxAnswer` circuit-breaker bounds, so a token or native-asset crash (LUNA-style) causes the paymaster to keep using a stale clamped price while `latestRoundData` still looks "fresh" and "positive".

### Finding Description
`_getOraclePrice` is the sole oracle-consumption path used for every pricing decision in the paymaster: [1](#0-0) 

It only reverts on `answer <= 0` or staleness beyond `maxOracleAge`; it does not compare `answer` against the aggregator's configured `minAnswer`/`maxAnswer`. Chainlink `AggregatorV3Interface` (as wired here, see the minimal interface declared at the top of the file) does not expose those bounds, and the contract makes no attempt to fetch or enforce them: [2](#0-1) 

This price feed drives `_tokenPrice`, which is called from the ERC-4337 validation hook `_fetchDetails` (executed once per submitted `UserOperation`, i.e., reachable by any unprivileged bandwidth purchaser paying gas through this paymaster): [3](#0-2) [4](#0-3) 

The same unchecked price also drives the treasury-only `swapAndDeposit` recycling path (less relevant here since it's privileged), but the validation-path exposure via `_fetchDetails`/`_prefund` is unprivileged and triggered by every submitted UserOp: [5](#0-4) 

If the underlying Chainlink feed for a registered ERC-20 (or the `nativeOracle`) hits its `minAnswer`/`maxAnswer` circuit breaker during a severe price move, `latestRoundData()` continues to report the clamped bound as a valid, timely answer. `_getOraclePrice` accepts it unconditionally, so `_tokenPrice` computes gas cost using a price that no longer reflects the asset's real market value.

### Impact Explanation
Because `_erc20Cost`/`_prefund` charge the user exactly `weiCost * tokenPrice / 1e18` using this unchecked oracle price, a token that has crashed far below its aggregator's `minAnswer` floor would still be priced by the paymaster as if it were worth the floor price. Any unprivileged submitter can then pay gas with a devalued/near-worthless registered token while the paymaster's `_prefund` pulls only the (undervalued-in-reality-but-overvalued-per-oracle) token amount and the paymaster spends real native funds from its EntryPoint deposit to cover the UserOp. This directly drains value from the paymaster's treasury/deposit — a concrete loss of funds reachable from a single submitted UserOperation, with no privileged action required. The `Permit2`-gated mode (0x02) even explicitly reasons about "a manipulated oracle" but only bounds the *signed* permit amount, not the oracle answer itself, so it does not close this gap.

### Likelihood Explanation
This requires the specific external condition of an underlying registered asset's price crashing through its Chainlink aggregator's hard-coded `minAnswer`/`maxAnswer` bound (real precedent: LUNA/UST crash tripped exactly this on several Chainlink feeds). It is not attacker-triggerable at will, but once the condition occurs it is trivially and immediately exploitable by any address able to submit a UserOp using the affected token, with no special privileges, for as long as governance has not yet deactivated the token via `DeactivateToken`.

### Recommendation
In `_getOraclePrice`, additionally fetch or hard-code each registered aggregator's `minAnswer`/`maxAnswer` (or query a wrapper/registry that exposes them) and revert (or fail closed / mark the token inactive) when `answer` is at or beyond those bounds, mirroring the mitigation Aave/Compound-style protocols adopted after the LUNA incident. As a defense-in-depth measure, also consider adding an automated or permissionless "circuit tripped" pause that deactivates a token when its oracle answer is detected pinned at a bound for longer than a short grace period, complementing the existing governance-only `DeactivateToken` recovery path.

### Proof of Concept
1. Governance registers token `T` with Chainlink feed `F` via `RegisterToken` (`_registerToken`).
2. `T`'s market price collapses (e.g., a LUNA-style depeg) to a small fraction of `F`'s configured `minAnswer`.
3. `F.latestRoundData()` keeps returning `minAnswer` as `answer`, with `updatedAt` still within `maxOracleAge` (aggregators typically keep updating on heartbeat/deviation triggers even while clamped).
4. Attacker submits a UserOperation with `paymasterData` mode `0x00` or `0x02` referencing `T`. `_fetchDetails` → `_tokenPrice` → `_getOraclePrice(F, ...)` returns the clamped (stale-relative-to-reality) `minAnswer`-derived price, far above `T`'s true worth.
5. `_prefund`/`_erc20Cost` charges the attacker `T` at the inflated oracle-derived rate; the paymaster's EntryPoint deposit covers the real native gas cost.
6. Because `T` is now nearly worthless on the open market, the attacker has obtained gas sponsorship (paid for out of the paymaster's real native funds) for a token cost that is economically negligible, repeatable for every UserOp until governance manually deactivates `T`.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L17-25)
```text
/// @notice Minimal Chainlink AggregatorV3 interface — no external dependency needed.
interface AggregatorV3Interface {
    function latestRoundData()
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);

    function decimals() external view returns (uint8);
}
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
