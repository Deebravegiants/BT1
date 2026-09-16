Confirmed: `SimplexPaymaster` is a "fully onchain, permissionless ERC-4337 v0.8 paymaster" [1](#0-0) , used by intent solvers/fillers to sponsor their gas via `PaymasterSelection`/`UserOpSender` in the simplex SDK [2](#0-1) . Its `_getOraclePrice` only checks `answer <= 0` and staleness, never comparing against the Chainlink aggregator's `minAnswer`/`maxAnswer` bounds [3](#0-2) , and this price directly sets both the per-UserOp token charge in `_tokenPrice`/`_fetchDetails` [4](#0-3) [5](#0-4)  and the `swapAndDeposit` slippage floor [6](#0-5) .

### Title
Missing Chainlink min/max price-bound check lets a crashed fee token be charged at its stale floor price - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster._getOraclePrice` only rejects a non-positive answer and a stale `updatedAt`; it never checks the returned `answer` against the underlying Chainlink aggregator's `minAnswer`/`maxAnswer` circuit-breaker bounds. During a severe depeg/crash of a registered ERC-20 fee token, the aggregator will keep reporting its clamped `minAnswer` (heartbeat and staleness checks still pass) rather than the real, much lower market price.

### Finding Description
`_getOraclePrice` normalizes and returns `answer` from `AggregatorV3Interface.latestRoundData()` after only two checks — `answer <= 0` and elapsed time since `updatedAt` — with no floor/ceiling comparison against the aggregator's configured bounds [3](#0-2) . `_tokenPrice` uses this value directly:

`tokenPrice = (nativeUsd * 10^tokenDecimals * (10000+markupBps)) / (tokenUsd * 10000)` [4](#0-3) 

If a registered token's true USD value collapses below the aggregator's `minAnswer`, `tokenUsd` stays pinned at the artificially high floor instead of falling with the market. Since `tokenPrice` (tokens charged per wei of gas) is inversely proportional to `tokenUsd`, an inflated `tokenUsd` produces an *understated* token charge: `_fetchDetails`/`_prefund` will charge users far fewer of the now near-worthless tokens than the gas actually costs the paymaster in native currency [7](#0-6) . The same stale/floored price also sets the `amountOutMin` slippage floor in `swapAndDeposit`, which converts accrued token fees back to native currency to refill the EntryPoint deposit [8](#0-7) ; the router would be forced to accept selling depreciated tokens at the stale, inflated USD reference, but liquidity/slippage limits mean this leg mostly bounds the treasury's own recycling rather than external exploitation.

The contract explicitly acknowledges general "malicious oracle" exposure and bounds it only via small permit amounts on the mode-0x00 path and the signed `permitAmount` cap on the Permit2 path [9](#0-8) ; however that mitigation targets a compromised/malicious *feed*, not this specific bug (a functioning, on-heartbeat Chainlink feed silently reporting its clamped floor during a genuine market crash). It does not fully close the gap since it only limits the attacker's *signed* exposure per call rather than the paymaster's realized economic loss from systematically undercharging users for gas paid out of the paymaster's own EntryPoint deposit and treasury.

### Impact Explanation
This is a permissionless surface: any ERC-4337 bundler/solver can submit UserOps against any registered fee token at any time, including during a live depeg. If a registered token (any current or future governance-approved ERC-20 with a Chainlink feed) crashes hard enough to hit its aggregator's `minAnswer`, every UserOp paid in that token will systematically undercharge, draining the paymaster's EntryPoint-deposited native funds and accumulated treasury value over the token's remaining active window until governance reacts and deactivates it. This is a genuine, ongoing loss of protocol funds rather than a one-off griefing event.

### Likelihood Explanation
Requires (a) a registered fee token whose Chainlink feed has (or later develops) a binding `minAnswer`/`maxAnswer`, and (b) that token's market price to actually reach that bound during a crash — a realistic, historically observed event (e.g., LUNA/UST, CRV, stablecoin depegs). Registration is governance-gated, so likelihood depends on which tokens are approved, but the check is entirely absent for any token, making this a systemic gap rather than a one-token edge case.

### Recommendation
Fetch and cache each registered oracle's `minAnswer`/`maxAnswer` (via `AggregatorV3Interface(oracle).aggregator()` or equivalent) at registration time, and have `_getOraclePrice` revert (e.g., `InvalidOraclePrice`) whenever `answer` is at or outside those bounds, mirroring the existing `answer <= 0` and staleness checks.

### Proof of Concept
1. Governance registers token `T` with Chainlink feed `F` whose aggregator has `minAnswer = $0.10`.
2. `T`'s real market price crashes to $0.001 due to a depeg event; `F.latestRoundData()` continues returning `answer = 0.10e8` (heartbeat/updatedAt still fresh, so `chainLinkIsDead`-equivalent staleness check in `_getOraclePrice` passes).
3. A solver/bundler submits UserOps paying gas in `T` via mode 0x00 or 0x02; `_tokenPrice` computes `tokenPrice` from the inflated `$0.10` instead of the real `$0.001`, so `_erc20Cost` charges roughly 100x too few `T` tokens for the same native gas cost.
4. Repeating this for the remainder of `T`'s registration window drains the paymaster's EntryPoint deposit/treasury in real native value while the paymaster's actual token holdings are worth a fraction of what was credited.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L55-58)
```text
/// @notice Fully onchain, permissionless ERC-4337 v0.8 paymaster that accepts
///         ERC-20 stablecoins (USDC, USDT, or any token with a Chainlink feed)
///         for gas payment. Deployed behind an ERC1967Proxy and administered
///         exclusively through Hyperbridge governance.
```

**File:** evm/src/utils/SimplexPaymaster.sol (L90-114)
```text
///      originating from Hyperbridge governance and delivered by the local
///      host. Clients additionally keep permit amounts small (a few dollars),
///      bounding exposure to the residual allowance even against a malicious
///      oracle.
///
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
///
///      Permit2 signatures name this contract as spender and are single-use,
///      so no third party can consume or burn them; only the signed
///      permitAmount is ever at risk, and only through {_prefund}. Permit2 must
///      never be reachable from any other entry point of this contract.
///
///      ERC-7562 note: Permit2's nonce bitmap and the token's Permit2 allowance
///      are not sender-associated storage, so spec-enforcing bundlers may reject
///      mode 0x02 during validation; only mode 0x00 remains for permit tokens.
```

**File:** evm/src/utils/SimplexPaymaster.sol (L464-480)
```text
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;

        address[] memory path = new address[](2);
        path[0] = token;
        path[1] = IUniswapV2Router02(router).WETH();

        IERC20(token).forceApprove(router, amountIn);
        uint256[] memory amounts = IUniswapV2Router02(router)
            .swapExactTokensForETH(amountIn, amountOutMin, path, address(this), block.timestamp);

        uint256 deposited = address(this).balance;
        entryPoint().depositTo{value: deposited}(address(this));
        emit FeesRecycled(token, amountIn, amounts[1], deposited);
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

**File:** sdk/packages/simplex/src/services/paymaster/provider/simplex.ts (L1-1)
```typescript
import {
```
