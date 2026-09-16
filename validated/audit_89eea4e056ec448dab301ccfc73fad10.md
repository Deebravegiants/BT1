### Title
Missing Arbitrum/Optimism L2 Sequencer-Uptime Check in `SimplexPaymaster` Oracle Pricing - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster` prices ERC-20 gas payments using Chainlink `latestRoundData()` calls that validate only positivity and staleness (`updatedAt` age), never consulting a Chainlink L2 Sequencer Uptime Feed. The paymaster is deployed on Optimistic-rollup chains (documented in `docs/content/developers/evm/contract-addresses/mainnet.mdx`, which references Arbitrum), so it is exposed to the classic sequencer-downtime staleness gap the Chainlink docs specifically warn L2 integrators about.

### Finding Description
`_getOraclePrice` only checks `answer <= 0` and `block.timestamp - updatedAt > maxOracleAge`: [1](#0-0) 

This is called by `_tokenPrice`, which is invoked from the permissionless `_fetchDetails` hook that runs for every ERC-4337 `UserOperation` presented to the paymaster (mode `0x00`/permit or mode `0x02`/Permit2), with no privileged gating: [2](#0-1) [3](#0-2) 

Any address that can submit a `PackedUserOperation` through an ERC-4337 bundler (an "unprivileged bandwidth purchaser" paying gas through this paymaster) reaches this pricing path with zero permissions required — no relayer/host/treasury gate applies to `_fetchDetails`/`_prefund`, unlike the governance-only `onAccept` path.

If the underlying chain is Arbitrum (or another Optimistic rollup with a Sequencer Uptime Feed), a sequencer outage prevents new transactions from being sequenced (aside from the slow L1 force-inclusion path) while the *last* Chainlink round remains within `maxOracleAge` and therefore still passes the staleness check. When the sequencer restarts, backlogged/queued UserOps (or transactions submitted immediately at restart, before Chainlink nodes push a fresh round) get priced off the stale round that predates the outage. Because `tokenPrice` (token units per wei of native gas) is derived purely from this stale ratio, an attacker can time a UserOp to land right as the sequencer resumes and pay in ERC-20 tokens at a price that no longer reflects the true native/USD or token/USD rate.

### Impact Explanation
The paymaster is fully on-chain solvent risk: `_erc20Cost` charges the token amount computed from `tokenPrice`, then reimburses the sender's actual native gas cost from the paymaster's EntryPoint deposit. A stale price during/after a sequencer outage lets a UserOp submitter underpay in the ERC-20 token relative to the true value of gas consumed from the paymaster's deposit, directly draining the paymaster's `entryPoint()` deposit (funded by the treasury) for the benefit of an opportunistic submitter — a concrete transfer of value out of protocol-controlled funds. This matches the Medium-severity "stale price enables value extraction from the protocol" pattern of the source report, mapped here onto the paymaster's own solvency rather than a lending protocol's collateral ratio.

### Likelihood Explanation
Requires an actual Arbitrum-class sequencer downtime event (rare but has occurred historically, e.g., past Arbitrum/Optimism outages), and precise timing by the attacker to submit during/at the recovery window before a fresh Chainlink round lands. This keeps likelihood at Medium rather than High: it is a real, externally-triggerable condition, not a routine occurrence, and the existing `maxOracleAge` bound already limits how stale a usable round can be, narrowing but not eliminating the exploit window (an outage shorter than `maxOracleAge` combined with volatile native/token prices is enough).

### Recommendation
Add a Chainlink `SequencerUptimeFeed` check (with the standard grace period, e.g. `GRACE_PERIOD_TIME`) in `_getOraclePrice`, reverting when the sequencer is down or still within its grace period after restart, mirroring the recommended pattern:
```solidity
(, int256 seqAnswer, uint256 seqStartedAt,,) = sequencerUptimeFeed.latestRoundData();
if (seqAnswer != 0 || block.timestamp - seqStartedAt <= GRACE_PERIOD_TIME) revert SequencerDown();
```
This should be wired into `Params`/`_setParams` (per-chain configurable, since not every deployment target is an Optimistic rollup) and enforced before trusting `latestRoundData()` in `_getOraclePrice`.

### Proof of Concept
1. Governance deploys `SimplexPaymaster` on Arbitrum via `DeploySimplexPaymaster.s.sol`, registering a native/USD and a token/USD Chainlink feed with `maxOracleAge` set to a multi-hour buffer (per the script's comment, up to ~25h for stablecoin heartbeats).
2. Arbitrum sequencer halts. During the halt, native asset price moves materially on other venues, but the last on-chain round remains within `maxOracleAge`.
3. Sequencer resumes; before a new Chainlink round is pushed, an attacker submits (or a queued L1-forced tx executes) a `UserOperation` with `paymasterData` mode `0x00`/`0x02` targeting a registered token.
4. `_fetchDetails` → `_tokenPrice` → `_getOraclePrice` return the stale, favorable ratio; `_erc20Cost`/`_prefund` charge the attacker less token value than the true native gas cost.
5. `postOp`/EntryPoint reimburse the actual (now higher) native gas cost from the paymaster's EntryPoint deposit, realizing a loss to the paymaster/treasury with each such transaction until a fresh round is pushed. [4](#0-3)

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
