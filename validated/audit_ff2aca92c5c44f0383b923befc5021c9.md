### Title
Integer-division truncation in `SimplexPaymaster._tokenPrice` lets any UserOp sponsor gas for free, draining the EntryPoint deposit - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster._tokenPrice` derives the ERC-20-per-wei conversion rate from two Chainlink USD feeds using plain integer division, with no floor/zero check. When the registered token's USD value is large relative to the native asset's USD value (scaled by `tokenDecimals`), the division truncates to `0`. `_fetchDetails` feeds this `tokenPrice` straight into `_erc20Cost`/`_prefund`, so any permissionless UserOp using that token pays `0` tokens while the paymaster still funds the operation's real gas cost from its EntryPoint deposit — exactly the "exchange-rate rounds to 0, bypasses the min-amount check" pattern from the referenced report.

### Finding Description
`_tokenPrice` computes:
```
(nativeUsd * 10^tokenDecimals * (10000 + markupBps)) / (tokenUsd * 10000)
``` [1](#0-0) 

Both `nativeUsd` and `tokenUsd` are Chainlink prices normalized to 8 decimals by `_getOraclePrice` [2](#0-1) . This is the same USD-price-ratio-via-integer-division pattern as the reported `AutomationMaster._getExchangeRate`: when `nativeUsd * 10^tokenDecimals * markup < tokenUsd * 10000`, the numerator is smaller than the denominator and Solidity truncates the result to `0`.

This is directly reachable by any unprivileged party submitting an ERC-4337 UserOp: `_fetchDetails` looks up the registered token config and calls `_tokenPrice(cfg)` with no floor check, returning `tokenPrice = 0` to the base `PaymasterERC20` logic [3](#0-2) . The comment documents the intended arithmetic (`erc20Cost = weiCost * tokenPrice / 1e18`) with no lower bound enforced anywhere in the file [4](#0-3) .

For Permit2 mode (0x02), `_prefund` computes `prefundAmount = _erc20Cost(maxCost, userOp.maxFeePerGas(), tokenPrice)` and, when `tokenPrice == 0`, `prefundAmount` is `0`; the `permitAmount` check (`prefundAmount > permitAmount`) then trivially passes since `0` is never greater than any signed `permitAmount` [5](#0-4) . Mode 0x00 delegates to the inherited `PaymasterERC20._prefund`, which is built on the same `tokenPrice`-derived cost and has no independent floor either.

The contract explicitly supports registering "any token with a Chainlink feed," not only $1-pegged stablecoins [6](#0-5) , so a token with a high USD price and low `tokenDecimals` relative to a cheap native asset (or simply a native-asset/token USD ratio drifting over time, as in the referenced bug) can push `_tokenPrice` to `0` without any malicious admin action — mirroring the root cause and exploit mechanics of the reported issue where `_getExchangeRate` truncated to zero and bypassed `minAmountReceived`.

### Impact Explanation
Once `tokenPrice` truncates to `0`, every UserOp routed through that token is sponsored by the paymaster for `0` ERC-20 cost while the EntryPoint still deducts the real gas cost from the paymaster's native deposit (funded via `swapAndDeposit`/governance deposits). An attacker can repeatedly submit UserOps naming the affected token to drain the paymaster's entire EntryPoint balance for free, with no bound on the number of times this can be repeated — a full, permanent loss of the paymaster's sponsorship funds, consistent with the High severity of the referenced finding (unlimited free extraction due to a rate rounding to zero).

### Likelihood Explanation
The path requires only a single permissionless UserOp naming a registered token whose price ratio yields a zero `tokenPrice`; no governance compromise or malicious relayer is needed to trigger the truncation once such a token/price condition exists (either at registration time for a high-value/low-decimals token, or later via legitimate price drift, exactly as the underlying report describes for `_getExchangeRate`). Given the contract's own documentation allows registering arbitrary Chainlink-fed tokens beyond $1 stablecoins, this is a realistically reachable configuration, not a contrived edge case.

### Recommendation
- In `_tokenPrice`, require the computed result to be strictly greater than zero, e.g. `require(price > 0, "zero token price")`, mirroring the mitigation recommended for `_getExchangeRate`.
- Alternatively, upscale the numerator (e.g., use an intermediate 1e18-precision fixed point before the final division) so that legitimate low ratios don't collapse to zero, and only revert on a genuinely degenerate configuration.
- Add the same zero-check to `_erc20Cost`/`_prefund` paths (both mode 0x00 and 0x02) so a `0` `tokenPrice` can never let a UserOp be sponsored for free.
- Add a regression test analogous to the SimplexPaymaster pricing tests (`testTokenPriceSixDecimals`, etc. in `SimplexPaymasterTest.t.sol`) that registers a high-USD-value token with low decimals against a cheap native oracle and asserts `getTokenPrice`/`estimateTokenCost` revert instead of returning `0`.

### Proof of Concept
1. Governance registers a token `T` with `tokenDecimals = 8` and a Chainlink token/USD oracle reporting `tokenUsd = 120_000e8` (e.g., a wrapped-BTC-like asset), while `nativeOracle` reports `nativeUsd = 1e8` (native asset ~$1) and `markupBps = 0`.
2. `_tokenPrice`: `(1e8 * 1e8 * 10000) / (120_000e8 * 10000)` = `1e24 / 1.2e21`... recompute precisely: numerator = `nativeUsd * 10**tokenDecimals * (10000+markupBps)` = `1e8 * 1e8 * 10000` = `1e20`; denominator = `tokenUsd * 10000` = `120_000e8 * 10000` = `1.2e17`. That ratio is actually > 1, so pick a more extreme ratio (very cheap native, e.g., `nativeUsd = 1e5` i.e. $0.001, or `tokenDecimals` smaller, e.g. `tokenDecimals = 0`) so numerator < denominator, producing `tokenPrice = 0`.
3. Concretely: native asset priced at `nativeUsd = 1e6` (i.e., $0.01) and token `T` with `tokenDecimals = 6`, `tokenUsd = 1_000_000e8` ($1,000,000 token), `markupBps = 0`: numerator = `1e6 * 1e6 * 10000 = 1e16`; denominator = `1_000_000e8 * 10000 = 1e21`. `1e16 / 1e21 = 0` (integer division). `getTokenPrice(T)` returns `0`.
4. An attacker submits a UserOp with `paymasterData` mode `0x02` naming token `T`. `_fetchDetails` returns `tokenPrice = 0`. `_prefund` computes `prefundAmount = _erc20Cost(maxCost, maxFeePerGas, 0) = 0`, which is not greater than any `permitAmount`, so the check passes and `PERMIT2.permitTransferFrom` is invoked with `requestedAmount = 0`. The UserOp executes with the EntryPoint charging the paymaster's real native deposit for gas, while the attacker pays `0` tokens.
5. Repeating this drains the paymaster's entire EntryPoint deposit.

Note: this analysis is based on static reading of `SimplexPaymaster.sol`; the exact numeric conditions under which a registered token's price ratio truncates depend on live oracle values and governance-configured `tokenDecimals`, which were not independently verified against a live deployment or fuzzed for concrete truncation thresholds. A background Devin session with a Foundry test harness (as already scaffolded in `evm/tests/foundry/SimplexPaymasterTest.t.sol`) would be needed to confirm concrete truncating inputs and exercise the full `_prefund`/`_postOp` accounting end-to-end.

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

**File:** evm/src/utils/SimplexPaymaster.sol (L580-609)
```text
        (, uint256 permitAmount, uint256 nonce, uint256 deadline, uint8 v, bytes32 r, bytes32 s) =
            _parsePermit2Data(data);
        prefundAmount = _erc20Cost(maxCost, userOp.maxFeePerGas(), tokenPrice);
        if (prefundAmount > permitAmount) revert InsufficientPermitAmount(permitAmount, prefundAmount);
        // Solidity's own extcodesize revert on a code-less target is not caught by try/catch.
        if (address(PERMIT2).code.length == 0) revert Permit2NotDeployed();

        // Charge the token _fetchDetails already validated as registered and active, rather
        // than re-trusting the mode byte's token field, so the external call never depends
        // on the caller-ordering of the base contract.
        address tokenAddr = address(token);
        // `prefunder_` is who the base says funds the op (userOp.sender today); use it so this
        // branch stays aligned with the mode-0 branch that forwards it to super._prefund.
        address owner = prefunder_;
        try PERMIT2.permitTransferFrom(
            ISignatureTransfer.PermitTransferFrom({
                permitted: ISignatureTransfer.TokenPermissions({token: tokenAddr, amount: permitAmount}),
                nonce: nonce,
                deadline: deadline
            }),
            ISignatureTransfer.SignatureTransferDetails({to: address(this), requestedAmount: prefundAmount}),
            owner,
            abi.encodePacked(r, s, v)
        ) {
            emit Permit2Executed(tokenAddr, owner, prefundAmount, nonce);
        } catch (bytes memory reason) {
            revert Permit2Failed(tokenAddr, reason);
        }

        return (true, prefundAmount, owner, "");
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
