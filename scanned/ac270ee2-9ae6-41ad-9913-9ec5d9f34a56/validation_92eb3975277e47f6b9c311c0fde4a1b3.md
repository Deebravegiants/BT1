### Title
`stakedButUnverifiedNativeETH` Not Reduced on Beacon-Chain Slashing Inflates rsETH Price Exposed via `RSETHPriceFeed` - (File: `contracts/NodeDelegator.sol`)

---

### Summary

`NodeDelegator.getEffectivePodShares()` sums `stakedButUnverifiedNativeETH` (incremented by exactly 32 ETH per `stake32Eth` call, decremented only on `verifyWithdrawalCredentials`) with the EigenLayer withdrawable share. If a validator is slashed on the beacon chain **before** its withdrawal credentials are verified, the actual ETH backing drops below 32 ETH, but `stakedButUnverifiedNativeETH` is never reduced. This inflated value propagates through `LRTDepositPool.getTotalAssetDeposits` → `LRTOracle._getTotalEthInProtocol` → `LRTOracle.rsETHPrice`, and is then published as a Chainlink-compatible price by `RSETHPriceFeed.latestRoundData`, allowing external lending protocols that accept rsETH as collateral to price it above its true redeemable value.

---

### Finding Description

**Step 1 — Inflation source: `stakedButUnverifiedNativeETH`**

Every call to `stake32Eth` unconditionally adds 32 ETH:

```solidity
// NodeDelegator.sol:166
stakedButUnverifiedNativeETH += 32 ether;
```

The only decrement path is `verifyWithdrawalCredentials`, which subtracts exactly `validatorFields.length * 32 ether`:

```solidity
// NodeDelegator.sol:240
stakedButUnverifiedNativeETH -= (validatorFields.length * (32 ether));
```

There is no code path that reduces `stakedButUnverifiedNativeETH` when a validator is slashed on the beacon chain during the unverified window.

**Step 2 — Inflation flows into `getEffectivePodShares`**

```solidity
// NodeDelegator.sol:556-561
function getEffectivePodShares() external view override returns (uint256 ethStaked) {
    uint256 withdrawableShare =
        NodeDelegatorHelper.getWithdrawableShare(lrtConfig, IStrategy(lrtConfig.beaconChainETHStrategy()));
    return stakedButUnverifiedNativeETH + withdrawableShare;
}
```

For unverified validators, `withdrawableShare` is 0 (EigenLayer has no record of them yet), so the entire `stakedButUnverifiedNativeETH` is counted at face value.

**Step 3 — Inflation flows into `_getTotalEthInProtocol` and `rsETHPrice`**

```solidity
// LRTDepositPool.sol:487
ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
```

```solidity
// LRTOracle.sol:250
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

`updateRSETHPrice()` is public and callable by anyone:

```solidity
// LRTOracle.sol:87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

**Step 4 — Inflated price published as Chainlink feed**

```solidity
// RSETHPriceFeed.sol:68-69
(roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
```

`RSETHPriceFeed` is a Chainlink `AggregatorV3Interface`-compatible contract that multiplies the stored `rsETHPrice` by the ETH/USD price. Any external lending protocol (Morpho, Aave, etc.) that uses `RSETHPriceFeed` as the rsETH/USD collateral oracle will read the inflated price.

**Why the existing price-protection does not help**

The downside circuit-breaker in `_updateRsETHPrice` pauses the protocol only when `newRsETHPrice < highestRsethPrice` by more than `pricePercentageLimit`. A slashing event during the unverified window does **not** cause the on-chain price to drop — it causes it to remain artificially high relative to the true backing. The upside guard only blocks non-manager callers when the price *increases* beyond the threshold. Neither guard fires for a price that is stale-high.

---

### Impact Explanation

**Impact: Medium — Temporary freezing of funds / theft of unclaimed yield**

1. **External lending protocols**: Any protocol using `RSETHPriceFeed` as a collateral oracle prices rsETH above its true redeemable value. Borrowers can open under-collateralised positions. When the slashing is eventually reflected (after `verifyWithdrawalCredentials` is called and a checkpoint is completed), the rsETH price drops, leaving the lending protocol with bad debt and legitimate lenders unable to recover their funds.

2. **New depositors**: `getRsETHAmountToMint` divides by the inflated `rsETHPrice`, so new depositors receive fewer rsETH tokens than the ETH they deposit warrants — a direct, silent loss of value.

3. **Existing holders**: Can redeem rsETH at the inflated price, extracting more ETH than their proportional share, at the expense of remaining holders.

---

### Likelihood Explanation

- EigenLayer restaking with native ETH requires a window between `stake32Eth` and `verifyWithdrawalCredentials` that can span days to weeks (beacon-chain finality, proof generation, operator scheduling).
- Beacon-chain slashing is a known, non-negligible risk for large validator sets (correlation penalties, client bugs, key mismanagement).
- `updateRSETHPrice()` is permissionless; any actor can trigger the price update that locks in the inflated value.
- The protocol already handles significant native ETH staking (`stake32Eth`, `stake32EthValidated`), making the unverified window a persistent, non-trivial exposure.

---

### Recommendation

1. **Track actual beacon-chain balance for unverified validators**: Instead of assuming 32 ETH per unverified validator, query the EigenPod's `currentCheckpointTimestamp` and `checkpointBalanceExitedGwei` or use `verifyStaleBalance` proofs to reduce `stakedButUnverifiedNativeETH` when a slashing event is proven on-chain.

2. **Cap `stakedButUnverifiedNativeETH` contribution**: Apply a conservative discount (e.g., the current `beaconChainSlashingFactor` from `IEigenPodManager`) to the unverified ETH when computing `getEffectivePodShares`.

3. **Circuit-breaker in `RSETHPriceFeed`**: Add a maximum staleness check on `rsETHPrice` (e.g., revert if `rsETHPrice` has not been updated within N hours) so external protocols cannot consume a stale-high price.

---

### Proof of Concept

1. Protocol stakes 100 validators via `stake32Eth` → `stakedButUnverifiedNativeETH = 3200 ETH`.
2. Before `verifyWithdrawalCredentials` is called, 10 validators are slashed on the beacon chain; their effective balance drops to ~28 ETH each (40 ETH lost).
3. `stakedButUnverifiedNativeETH` remains 3200 ETH (no on-chain mechanism reduces it).
4. Anyone calls `updateRSETHPrice()`. `_getTotalEthInProtocol()` returns a value 40 ETH higher than the true backing. `rsETHPrice` is set to the inflated value.
5. `RSETHPriceFeed.latestRoundData()` returns `rsETHPrice * ETH_USD / 1e18` — inflated by ~1.25%.
6. A borrower deposits rsETH as collateral in a Morpho/Aave market using `RSETHPriceFeed`. They borrow against the inflated collateral value, receiving more than the true backing supports.
7. When `verifyWithdrawalCredentials` is eventually called for the slashed validators, EigenLayer awards shares for only ~28 ETH each. The next `updateRSETHPrice()` call reflects the true (lower) backing, the rsETH price drops, and the lending protocol is left with under-collateralised positions.

**Key code references:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/NodeDelegator.sol (L165-166)
```text
        // tracks staked but unverified native ETH
        stakedButUnverifiedNativeETH += 32 ether;
```

**File:** contracts/NodeDelegator.sol (L235-240)
```text
        if (stakedButUnverifiedNativeETH < validatorFields.length * (32 ether)) {
            revert InsufficientStakedBalance();
        }

        // reduce the eth amount that is verified
        stakedButUnverifiedNativeETH -= (validatorFields.length * (32 ether));
```

**File:** contracts/NodeDelegator.sol (L556-562)
```text
    function getEffectivePodShares() external view override returns (uint256 ethStaked) {
        uint256 withdrawableShare =
            NodeDelegatorHelper.getWithdrawableShare(lrtConfig, IStrategy(lrtConfig.beaconChainETHStrategy()));

        // staker balances can no longer be negative
        return stakedButUnverifiedNativeETH + withdrawableShare;
    }
```

**File:** contracts/LRTDepositPool.sol (L484-493)
```text
        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
            unchecked {
                ++i;
            }
        }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L231-250)
```text
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/oracles/RSETHPriceFeed.sol (L63-70)
```text
    function latestRoundData()
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
    {
        (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
        answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
    }
```
