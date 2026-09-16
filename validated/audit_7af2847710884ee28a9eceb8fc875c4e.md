## Analysis: Sequencer-downtime price-staleness gap in `SimplexPaymaster`

The reachable, unprivileged-transaction analog to the Notional `ChainlinkAdapter` sequencer-uptime bug lives in `SimplexPaymaster`'s Chainlink price consumption, which is deployed on Arbitrum, Optimism, and Base — all Sequencer-based L2s using Chainlink feeds [1](#0-0) .

### Title
Missing L2 Sequencer-Uptime check in `SimplexPaymaster` Chainlink price consumption enables theft of paymaster funds during sequencer outages - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster._getOraclePrice` only validates that a Chainlink answer is positive and that `updatedAt` is within `maxOracleAge`; it never checks whether the L2 sequencer (Arbitrum/Optimism/Base) was recently down, per Chainlink's recommended `L2 Sequencer Uptime Feed` pattern [2](#0-1) .

### Finding Description
Any user (via a bundler) can submit a `PackedUserOperation` that is priced by `fetchDetails`/`_prefund`, both of which derive `tokenPrice` from `_tokenPrice` → `_getOraclePrice` for both the native/USD and token/USD feeds [3](#0-2) . The only safety check is a staleness bound on `updatedAt`:
```
if (block.timestamp - updatedAt > maxOracleAge) revert StaleOraclePrice(...)
```
This check is defeated by the exact sequencer-offline scenario described in the source report: when an L2 sequencer stalls, the last on-chain Chainlink `updatedAt` can remain "fresh" (within `maxOracleAge`, which the contract's own comment notes may be configured up to 24h for Base/Ethereum stablecoins) [4](#0-3)  while the real off-chain market price has already diverged sharply. Once the sequencer resumes, backlogged/delayed-inbox transactions execute first (Arbitrum's delayed-inbox behavior referenced in the source report), letting a submitter get their `UserOperation` processed against the stale price before a corrective price update lands.

Because `_prefund`/`_erc20Cost` size the ERC-20 amount pulled from the user strictly from this potentially-stale `tokenPrice` [5](#0-4) , and the same price feeds gas-cost estimation view functions relied on by clients/bundlers [6](#0-5) , an attacker can exploit the stale/mispriced window to pay far less (in token terms) than the real cost of gas the paymaster subsidizes from its EntryPoint deposit, or manipulate the recycling swap's `expectedWei` calc in `swapAndDeposit` [7](#0-6) .

Note the project itself explicitly deferred related oracle-freshness hardening ("oracle-derived validity bounds") as out of scope in a past change [8](#0-7) , confirming the gap is a live, unaddressed condition rather than mitigated elsewhere.

### Impact Explanation
This is a direct fund-loss path: the paymaster's EntryPoint-staked native balance and treasury-held ERC-20 surplus can be drained by users who submit gas-sponsored UserOperations priced off a stale Chainlink answer during/around a sequencer outage on Arbitrum, Optimism, or Base, satisfying "concrete theft ... of funds."

### Likelihood Explanation
Sequencer outages on Arbitrum/Optimism/Base, while infrequent, are a recurring, documented operational event (this is precisely why Chainlink ships the L2 Sequencer Uptime Feed and why AAVE V3 added a grace-period sentinel). Exploitation requires no privilege — any address can submit a UserOperation through a bundler — only the timing of a sequencer outage/restart, making this a real, externally-triggerable condition rather than a purely theoretical one.

### Recommendation
Integrate Chainlink's `L2 Sequencer Uptime Feed` in `_getOraclePrice` (or a wrapper), rejecting/pausing price reads if the sequencer is currently down or came back online within a grace period, mirroring AAVE V3's `PriceOracleSentinel` pattern referenced in the source report.

### Proof of Concept
1. Deploy `SimplexPaymaster` on Arbitrum with `maxOracleAge` set to a multi-hour value as its own comment allows [4](#0-3) .
2. Arbitrum sequencer goes offline while the underlying market price of a registered token/native asset moves sharply; the on-chain Chainlink `updatedAt` remains within `maxOracleAge`.
3. Attacker submits a UserOperation (directly to Arbitrum's delayed inbox if needed) that gets processed by `fetchDetails`/`_prefund`, pricing the sponsored gas off the now-incorrect but not-yet-"stale" oracle value [9](#0-8) .
4. Attacker's op is executed once the sequencer resumes and processes the backlog before any corrective price update lands, extracting subsidized gas value at the paymaster's expense.

### Citations

**File:** sdk/packages/indexer/src/addresses/chainlink-price-feeds.addresses.ts (L5-14)
```typescript
	"EVM-84532": "0x4aDC67696bA383F43DD60A9e78F2C97Fbbfc7cb1", // Base Sepolia
	"EVM-11155420": "0x61Ec26aA57019C486B10502285c5A3D4A4750AD7", // Optimism Sepolia
	"EVM-421614": "0xd30e2101a97dcbAeBCBC04F14C3f624E67A35165", // Arbitrum Sepolia
	"EVM-97": "0x2514895c72f50D8bd4B4F9b1110F0D6bD2c97526", // BSC Chapel

	"EVM-1": "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419", // Ethereum Mainnet
	"EVM-8453": "0x71041dddad3595F9CEd3DcCFBe3D1F4b0a16Bb70", // Base Mainnet
	"EVM-10": "0x13e3Ee699D1909E989722E753853AE30b17e08c5", // Optimism Mainnet
	"EVM-42161": "0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612", // Arbitrum Mainnet
	"EVM-56": "0x0567F2323251f0Aab15c8dFb1967E4e8A7D42aeE", // BSC Mainnet
```

**File:** evm/src/utils/SimplexPaymaster.sol (L146-148)
```text
        /// @notice Maximum oracle staleness. Chainlink heartbeats vary per chain
        ///         (BSC stablecoins ~27s, Base/Ethereum stablecoins up to 24h).
        uint256 maxOracleAge;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L464-467)
```text
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L562-583)
```text
    ///      more than the solver signed.
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

**File:** evm/src/utils/SimplexPaymaster.sol (L689-697)
```text
    /// @notice Estimate the token cost for a given gas amount and fee, mirroring
    ///         PaymasterERC20._erc20Cost (including its postOp gas cushion).
    function estimateTokenCost(address token, uint256 gasAmount, uint256 maxFeePerGas) external view returns (uint256) {
        TokenConfig memory cfg = tokenConfigs[token];
        if (address(cfg.tokenOracle) == address(0)) revert TokenNotRegistered(token);

        uint256 weiCost = gasAmount * maxFeePerGas + _postOpCost() * maxFeePerGas;
        return (weiCost * _tokenPrice(cfg)) / _tokenPriceDenominator();
    }
```

**File:** sdk/packages/simplex/docs/ai/decisions/2026-08-19-not-adopted-soft-failing-the-prefund-and-oracle-derived.md (L1-5)
```markdown
# 2026-08-19 — Not adopted: soft-failing the prefund, and oracle-derived validity bounds (#1071)

Rejected: returning `prefunded = false` instead of reverting in the mode-2 `_prefund`. Upstream advises it to protect bundler reputation, but reading EntryPoint v0.8 shows both outcomes are `revert FailedOp` — AA33 for a paymaster revert, AA34 for a sig-failure — so both revert `handleOps` identically. The change would trade the `Permit2Failed(token, reason)` diagnostic, which carries Permit2's own revert data, for no bundle-level benefit.

Also deferred at the maintainer's direction: bounding `validationData`'s `validUntil` by oracle freshness so bundlers drop soon-to-be-stale ops instead of building bundles that revert. Sound in principle and would have made stale-oracle failures expire cleanly, but it touches every pricing path and was out of scope for this pass.
```
