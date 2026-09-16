I have enough evidence to produce a validated analog.

### Title
Missing Chainlink L2 sequencer-uptime check in `SimplexPaymaster._getOraclePrice()` used for gas pricing on Arbitrum/Base - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster` prices ERC-20 gas payments for any UserOperation using two Chainlink `AggregatorV3Interface` feeds (`nativeOracle` and the per-token `tokenOracle`) via `_getOraclePrice()`. This function only checks that `answer > 0` and that `block.timestamp - updatedAt <= maxOracleAge`; it never checks a Chainlink L2 sequencer-uptime feed, even though the paymaster is deployed on Arbitrum and Base, both of which are Chainlink-recommended-sequencer-check L2s.

### Finding Description
`_getOraclePrice()` is the sole gate on oracle validity for every price used by the paymaster: [1](#0-0) 

That price feeds `_tokenPrice()`, which is called from `_fetchDetails()` (executed during ERC-4337 validation of every sponsored UserOperation) and from `swapAndDeposit()` (fee-recycling swap sizing): [2](#0-1) [3](#0-2) [4](#0-3) 

No L2 sequencer-uptime feed (`AggregatorV2V3Interface` for the sequencer status) is read anywhere in the contract, and no `SequencerDown`/grace-period error exists — only `StaleOraclePrice` and `InvalidOraclePrice` are defined. [5](#0-4) 

Per Chainlink's own guidance for L2s (referenced by the external report), when the sequencer is down or has just recovered, `updatedAt`/`block.timestamp` staleness checks alone are insufficient: L2 block timestamps can advance in lock-step with a degraded sequencer state or jump discontinuously on recovery, letting a stale-but-"fresh-looking" price pass the `maxOracleAge` check, or letting a just-recovered feed be used before it re-stabilizes.

This contract is confirmed live on Arbitrum (`SimplexPaymaster: 0x7281Bccb...`) and documented as deployed/being deployed on Arbitrum and Base mainnets, both requiring the L2 sequencer-feed pattern: [6](#0-5) [7](#0-6) [8](#0-7) 

The deploy script's own comment shows the staleness bound was only tuned for L1/Base heartbeat cadence, not sequencer-outage semantics: [9](#0-8) 

### Impact Explanation
`SimplexPaymaster` is a permissionless, ERC-4337 paymaster: any solver can submit a UserOperation that gets priced by `_fetchDetails`/`_tokenPrice`. If Arbitrum's or Base's sequencer goes down and recovers, a stale or momentarily-distorted Chainlink price can be accepted as valid (it passes both the positivity and staleness checks), letting an attacker time a sponsored UserOperation to pay drastically less stablecoin than the actual native-gas cost, draining value from the paymaster's treasury/EntryPoint deposit — a concrete loss of protocol funds. The same stale price also feeds `swapAndDeposit`'s slippage-bounded swap, risking an unfavorable swap execution during the outage window. This is High severity: unbacked economic loss to a permissionless, protocol-operated contract reachable from a single relayed UserOperation.

### Likelihood Explanation
Likelihood is Medium: it requires an L2 sequencer outage/recovery event (which has occurred historically on Arbitrum/Optimism) coinciding with an attacker's readiness to submit a UserOperation through the paymaster during that exact window. It requires no privileged access — only a solver/user able to submit a normal sponsored UserOperation, which is the paymaster's designed permissionless entry point.

### Recommendation
Add a Chainlink L2 sequencer-uptime feed check (per-chain, governance-configurable like `nativeOracle`/`tokenOracle`) inside `_getOraclePrice()` (or a shared guard called before it), reverting with a new `SequencerDown`/`GracePeriodNotOver` error when `answer != 0` (sequencer down) or when `block.timestamp - startedAt` is within the recommended grace period (e.g., 3600s), mirroring Chainlink's reference implementation, for every chain where such a feed exists (Arbitrum, Base, Optimism, etc.).

### Proof of Concept
1. Deploy/observe `SimplexPaymaster` on Arbitrum with `nativeOracle`/`tokenOracle` set to real Chainlink feeds and `maxOracleAge` per `DeploySimplexPaymaster.s.sol` defaults.
2. Simulate an Arbitrum sequencer outage (e.g., via a forked test that manipulates `block.timestamp` progression while freezing oracle `updatedAt`, mirroring documented sequencer-halt behavior) such that `block.timestamp - updatedAt` stays within `maxOracleAge` despite the feed being stale relative to real-world price movement.
3. Submit a sponsored UserOperation through `_fetchDetails`/`getTokenPrice` during this window; observe that `_getOraclePrice()` returns the stale price without reverting, because it only checks `answer <= 0` and staleness against `maxOracleAge`: [10](#0-9) 
4. Confirm the resulting `tokenPrice` diverges materially from the true, sequencer-restored market price, letting the UserOperation's sponsor underpay (or the treasury overpay in `swapAndDeposit`).

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L226-232)
```text
    error TokenNotRegistered(address token);
    error TokenNotActive(address token);
    error StaleOraclePrice(address oracle, uint256 updatedAt);
    error InvalidOraclePrice(address oracle, int256 price);
    error InvalidMarkup(uint256 bps);
    error InvalidOracleAge(uint256 age);
    error InvalidSlippage(uint256 bps);
```

**File:** evm/src/utils/SimplexPaymaster.sol (L464-467)
```text
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;
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

**File:** evm/src/utils/SimplexPaymaster.sol (L651-658)
```text
    // ── Pricing ──────────────────────────────────────────────────────

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

**File:** sdk/packages/sdk/src/configs/chain.ts (L536-539)
```typescript
			EntryPointV08: "0x4337084D9E255Ff0702461CF8895CE9E3b5Ff108",
			CirclePaymaster: "0x0578cFB241215b77442a541325d6A4E6dFE700Ec",
			SimplexPaymaster: "0x7281Bccb4f0BCE44F3B8542d1fC5e51c2F5fC08C",
			Usdt0Oft: "0x14E4A1B13bf7F943c8ff7C51fb60FA964A298D92",
```

**File:** sdk/packages/simplex/docs/ai/decisions/2026-09-07-the-paymaster-relayer-is-governance-relayer-and-the-release.md (L8-16)
```markdown
Release order: live Ethereum, Base and Polygon proxies predate `PERMIT2()`, and the configured BSC
and Arbitrum addresses have no code. The filler never funds an EntryPoint deposit on a chain with a
Simplex address configured and `prepareBidUserOp` still submits a bid when selection ends with no
paymaster, so a USDT-only solver on those chains is unsponsored in either ordering: this client
before the proxy upgrade throws in the builder, the previous client after the upgrade sends mode 1
and fails validation. USDC has permit on all three, so it is USDT-only solvers either way. Rule:
deploy the implementation with `DeploySimplexPaymasterImpl.s.sol`, `upgrade_paymaster` with
`migrate(relayer)` init data on the three proxies, fresh deploys on BSC and Arbitrum, and only then
tag `simplex-v0.14.0`. A guard that skips the bid when no paymaster is usable was left out as a
```

**File:** docs/content/developers/evm/simplex/configuration.mdx (L79-82)
```text
Solver selection requires each solver's EOA to be delegated to the `SolverAccount` contract. Simplex performs this automatically at startup via EIP-7702:

- **Primary path** — builds a no-op UserOperation with an attached EIP-7702 authorization and submits it through the configured bundler. When a paymaster is deployed on the chain — Circle Paymaster (USDC) preferred, then the `SimplexPaymaster` (USDC or USDT), live on Ethereum, Arbitrum, Base, Polygon and BSC — see [Mainnet Contract Addresses](/developers/evm/contract-addresses/mainnet) — and the solver holds at least one whole token of a supported stablecoin, the paymaster pays gas in that stablecoin so the solver never needs native gas for delegation. Tokens with EIP-2612 are authorized by permit; tokens without it (such as BSC stables) need a one-time funded `approve(Permit2, max)` from the solver EOA, after which every operation carries a per-op Permit2 signature and no native gas is ne ... (truncated)
- **Fallback** — if the bundler path fails or the chain has no paymaster, Simplex sends a direct type-0x04 delegation tx using the solver's native balance. On paymaster-less chains it also keeps the ERC-4337 EntryPoint deposit topped up to cover `targetGasUnits` (default 3,000,000) at the current gas price.
```

**File:** evm/script/DeploySimplexPaymaster.s.sol (L17-20)
```text
        address treasury = vm.envOr("TREASURY", admin); // default to deployer
        // Stablecoin feeds on Ethereum and Base run a 24h heartbeat; a buffer over
        // 24h avoids transient StaleOraclePrice reverts on late pushes.
        uint256 maxOracleAge = vm.envOr("MAX_ORACLE_AGE", uint256(90_000));
```
