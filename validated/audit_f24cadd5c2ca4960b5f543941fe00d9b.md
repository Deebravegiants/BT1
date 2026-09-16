### Title
SimplexPaymaster's `_getOraclePrice()` doesn't validate Chainlink answer against aggregator min/max circuit-breaker bounds - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster._getOraclePrice()` fetches `latestRoundData()` from a Chainlink `AggregatorV3Interface` for both the native asset and each registered ERC-20 payment token, and only checks that the answer is positive and not stale. It never checks the returned `answer` against the aggregator's `minAnswer`/`maxAnswer` circuit-breaker bounds, which is exactly the bug class in the referenced Tokemak report.

### Finding Description
`_getOraclePrice` is defined at [1](#0-0)  and only validates:
```solidity
if (answer <= 0) revert InvalidOraclePrice(address(oracle), answer);
if (block.timestamp - updatedAt > maxOracleAge) {
    revert StaleOraclePrice(address(oracle), updatedAt);
}
```
There is no check that `answer` sits strictly between the feed's configured `minAnswer` and `maxAnswer`. Chainlink aggregators internally clamp reported answers to these bounds; during a sharp de-peg or flash crash of a registered payment token, the feed keeps returning the (now-stale-in-value) `minAnswer` floor, which is both positive and "fresh" (the feed still updates the round with the clamped value, so the staleness check does not catch it either).

This price is consumed directly in `_tokenPrice()` to compute the ERC-20 amount charged per unit of gas: [2](#0-1)  and again in `swapAndDeposit()` for the fee-recycling swap's minimum-output calculation: [3](#0-2) .

The paymaster is a permissionless ERC-4337 v0.8 paymaster that "accepts ERC-20 stablecoins (USDC, USDT, or any token with a Chainlink feed) for gas payment" per its own doc comment, and is documented as being usable by intent solvers submitting bids through the Simplex/coprocessor flow (referenced as "Simplex paymaster's PERMIT2 mode" in the phantom-bid aggregation logic) [4](#0-3) . Any address can submit a `PackedUserOperation` naming a registered token, so this is reachable by an unprivileged UserOp sender/solver without any governance action.

### Impact Explanation
If a registered payment token depegs or crashes below the Chainlink feed's `minAnswer` floor (e.g. a stablecoin collapse or an oracle-token bridge compromise), `tokenUsd` in `_tokenPrice()` continues to report the clamped floor price instead of the real, much lower price. Since `tokenUsd` sits in the denominator of the token-per-gas price formula, an inflated `tokenUsd` produces an under-priced amount of tokens charged to sponsor the UserOp's gas. An attacker can then:
- Acquire the crashed token cheaply on the open market,
- Submit UserOps paying gas with that token through `SimplexPaymaster`, extracting real native-asset-funded gas sponsorship while paying with tokens worth far less than what the paymaster's accounting assumes,
- Repeat until the paymaster's `EntryPoint` deposit / treasury surplus is drained relative to the real value of tokens it is receiving.

The same flawed price also feeds `swapAndDeposit()`'s slippage-protected minimum output, so a stale-floor price could similarly mis-price the treasury's fee-recycling swap.

### Likelihood Explanation
This requires an actual sharp de-peg/crash of one of the registered ERC-20 tokens (or its Chainlink feed) below the aggregator's configured floor — a real-world tail event but one Chainlink explicitly documents and one prior incidents (e.g. UST/USDC depeg events) have triggered on live feeds. Given the paymaster is deliberately permissionless (any UserOp sender can use it) and governance only controls token registration/oracle selection (not per-transaction validation), likelihood is Medium, matching the referenced report's own Medium severity classification for the identical root cause.

### Recommendation
In `_getOraclePrice()`, additionally read and enforce the aggregator's `minAnswer`/`maxAnswer` bounds (e.g., via `AggregatorV2V3Interface(oracle).minAnswer()`/`maxAnswer()` or a governance-configured bound per token), reverting when `answer <= minAnswer || answer >= maxAnswer`, mirroring the fix recommended in the source report.

### Proof of Concept
1. Governance registers token `T` with Chainlink feed `F` via `RegisterToken` (`_registerToken`, [5](#0-4) ).
2. `T` suffers a flash crash; `F`'s underlying aggregator clamps its reported `answer` to `minAnswer` (a positive, non-stale value) even though `T`'s real market price has fallen far below that floor.
3. Attacker buys `T` cheaply on a DEX.
4. Attacker submits a `PackedUserOperation` with mode `0x00`/`0x02` paymasterData naming `T`; `fetchDetails`/`validate` call `_tokenPrice(cfg)` → `_getOraclePrice(cfg.tokenOracle, ...)`, which returns the inflated `minAnswer`-based `tokenUsd`.
5. `SimplexPaymaster` charges the attacker `T` tokens computed from the inflated price, sponsoring the UserOp's real native gas cost while receiving tokens worth a fraction of that value, extracting the difference from the paymaster's EntryPoint deposit/treasury.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L53-69)
```text
/// @title  SimplexPaymaster
/// @author Polytope Labs
/// @notice Fully onchain, permissionless ERC-4337 v0.8 paymaster that accepts
///         ERC-20 stablecoins (USDC, USDT, or any token with a Chainlink feed)
///         for gas payment. Deployed behind an ERC1967Proxy and administered
///         exclusively through Hyperbridge governance.
///
/// Modes (byte 0 of paymasterData):
///   0x00  PERMIT  — EIP-2612 permit signature included; the permit is executed
///                    during validation so the subsequent prefund transferFrom
///                    succeeds without a prior onchain approval.
///   0x02  PERMIT2 — Permit2 SignatureTransfer signature included; the prefund
///                    is pulled through Permit2.permitTransferFrom, so the token
///                    only needs a one-time approval to Permit2 (the path for
///                    tokens without permit support, e.g. BSC stablecoins).
///   Any other mode byte, including the retired 0x01 that spent a standing
///   allowance to this contract, is refused with {InvalidMode}.
```

**File:** evm/src/utils/SimplexPaymaster.sol (L387-404)
```text
    function _registerToken(address token, AggregatorV3Interface oracle) internal {
        if (token == address(0) || address(oracle) == address(0)) revert ZeroAddress();

        bool isNew = !tokenConfigs[token].active && address(tokenConfigs[token].tokenOracle) == address(0);

        tokenConfigs[token] = TokenConfig({
            tokenOracle: oracle,
            tokenOracleDecimals: oracle.decimals(),
            tokenDecimals: IERC20Metadata(token).decimals(),
            active: true
        });

        if (isNew) {
            registeredTokens.push(token);
        }

        emit TokenRegistered(token, address(oracle));
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L464-467)
```text
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;
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
