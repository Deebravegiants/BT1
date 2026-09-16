## Analog Found

### Title
`SimplexPaymaster` prices ERC-4337 gas using Chainlink `latestRoundData()` without validating `minAnswer`/`maxAnswer` bounds - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster._getOraclePrice` fetches Chainlink price data and checks only that the answer is positive and not stale by timestamp, exactly the same gap the M-21 report identified in `ChainlinkOracle._getPriceWithSanityChecks`. It never checks the returned `answer` against the feed's `minAnswer`/`maxAnswer` bounds, so a price that has crashed (or spiked) past the aggregator's floor/ceiling is silently accepted as the "current" price even though Chainlink continues to report the clamped boundary value with a fresh `updatedAt`.

### Finding Description
`_getOraclePrice` is the sole gate on Chainlink data used to price gas payments in this ERC-4337 paymaster: [1](#0-0) 

It only validates `answer <= 0` and staleness derived from `updatedAt`, mirroring the exact pattern flagged in the referenced Sherlock report. Many production Chainlink feeds (as documented in M-21, e.g. BNB/USD) still enforce `minAnswer`/`maxAnswer` clamps at the aggregator level: when the true market price moves outside that range, the feed keeps publishing the boundary value with an up-to-date `updatedAt`, so the timestamp-based staleness check here never fires.

This price feeds directly into `_tokenPrice`, which every unprivileged UserOp submitter triggers through `_fetchDetails` on every paymaster-sponsored operation: [2](#0-1) [3](#0-2) 

The contract's own documentation acknowledges oracle risk only in the narrow context of bounding a *malicious* oracle's exposure to the permit allowance, not the clamped-price scenario: [4](#0-3) 

That mitigation doesn't help here: `_prefund`'s bound (`prefundAmount > permitAmount`) only prevents the paymaster from pulling *more* tokens than the signer authorized — it does nothing to stop the paymaster from accepting *too few* tokens relative to the real gas cost it pays out of its EntryPoint deposit.

### Impact Explanation
`tokenPrice = (nativeUsd * 10^tokenDecimals * (10000+markupBps)) / (tokenUsd * 10000)`. Any token "with a Chainlink feed" can be registered per the contract's own docstring (`evm/src/utils/SimplexPaymaster.sol:56`), including volatile, low-liquidity assets far more likely to hit a feed's `minAnswer` floor than a major asset like ETH/BNB.

- If the registered token's `tokenUsd` crashes below the feed's `minAnswer`, the feed keeps reporting the (higher) clamped `minAnswer` as current. `tokenPrice` is computed as artificially **low** (inversely proportional to `tokenUsd`), so every UserOp sponsored with that token charges far fewer token units than the real cost of the native gas the paymaster actually spends from its EntryPoint deposit.
- Any unprivileged party can submit UserOps against this paymaster (the permissionless "bandwidth purchaser" role for ERC-4337 gas), so an attacker can spam gas-sponsored operations paid for in the crashed token, draining the paymaster's EntryPoint-staked native balance and accrued treasury funds at a steep discount, while paying with a token that's rapidly losing (or has lost) real value.
- Symmetrically, if `nativeUsd` (native/USD oracle) is clamped above the real crashed native price, all users are systematically overcharged in the ERC-20 fee token relative to true gas cost, harming legitimate paymaster users.

This is a concrete draining/loss-of-funds vector reachable from a single unprivileged UserOp submission, matching the Medium-severity classification Sherlock ultimately assigned to the analogous `ChainlinkOracle` issue.

### Likelihood Explanation
Likelihood depends on (a) governance registering a token whose Chainlink feed enforces `minAnswer`/`maxAnswer` clamps (explicitly anticipated by the contract's own "any token with a Chainlink feed" design) and (b) that asset experiencing a price move past the clamp — a real, recurring Chainlink behavior documented for numerous live feeds (as cited in the M-21 report). No special privilege, governance compromise, or malicious relayer is required; any address can submit a UserOp naming the affected token once it crashes.

### Recommendation
In `_getOraclePrice` (and any other Chainlink consumer in this codebase, e.g. `swapAndDeposit`'s use of the same helper), additionally fetch and check the aggregator's configured `minAnswer`/`maxAnswer` (via `IAggregatorV3` extended to `AggregatorV2V3Interface` / `IChainlinkAggregator`, or a governance-configured allowed range per feed) and revert or fall back to a circuit-breaker state when `answer` is at or beyond those bounds, rather than trusting `latestRoundData()` at face value.

### Proof of Concept
1. Governance registers `TokenX` with a Chainlink `TokenX/USD` feed that enforces `minAnswer = $0.10` (a common pattern for feeds guarding against near-zero readings), via `RegisterToken` (`evm/src/utils/SimplexPaymaster.sol:124-125`, `initialize`/governance flow).
2. `TokenX`'s real market price crashes to $0.001. The Chainlink aggregator, hitting its floor, continues to report `answer = minAnswer ($0.10)` with a fresh `updatedAt` every heartbeat — passing both the `answer <= 0` and staleness checks in `_getOraclePrice` (`evm/src/utils/SimplexPaymaster.sol:662-676`).
3. `_tokenPrice` computes `tokenPrice` using the clamped $0.10 figure instead of the real $0.001, making `TokenX` appear ~100x more valuable than it is, so `_erc20Cost` charges the UserOp sender ~100x fewer `TokenX` units than the true USD-equivalent cost of gas.
4. Attacker (any unprivileged UserOp sender) repeatedly submits `TokenX`-paid UserOps via mode `0x00`/`0x02` (`_fetchDetails`, `_prefund` at `evm/src/utils/SimplexPaymaster.sol:524-610`), paying a small amount of near-worthless `TokenX` while the paymaster's EntryPoint deposit (funded by real native assets) is debited at the true, much higher gas cost — draining the paymaster.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L84-93)
```text
/// @dev Security model. The only allowance a solver ever holds towards this
///      contract is the residue of a mode 0x00 permit, bounded by the signed
///      permitAmount; mode 0x02 leaves none. A compromise must never translate
///      into large withdrawals from solver accounts. There is no privileged
///      key: every administrative action — upgrades, parameter changes, token
///      registry, withdrawals — is an onAccept request authenticated as
///      originating from Hyperbridge governance and delivered by the local
///      host. Clients additionally keep permit amounts small (a few dollars),
///      bounding exposure to the residual allowance even against a malicious
///      oracle.
```

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
