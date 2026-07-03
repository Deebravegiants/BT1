### Title
Incorrect `previousTVL` Calculation Using Current rsETH Supply Overstates Protocol Fee — (`contracts/LRTOracle.sol`)

---

### Summary

In `LRTOracle._updateRsETHPrice()`, the "previous TVL" baseline used to detect yield growth is computed with the **current** `rsethSupply` (which may have already decreased due to rsETH burns from withdrawal unlocking) multiplied by the **old** stored `rsETHPrice`. When rsETH has been burned between two price updates while the backing ETH remains in `LRTUnstakingVault` (still counted in `totalETHInProtocol`), the baseline is understated, the apparent reward is overstated, and the protocol mints more fee rsETH to the treasury than it is entitled to — stealing yield from all rsETH holders.

---

### Finding Description

`_updateRsETHPrice()` computes the previous TVL as:

```solidity
uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);
```

`rsethSupply` is the **live** total supply at the moment of the call, while `rsETHPrice` is the price stored from the **previous** update. These two values belong to different points in time.

The withdrawal lifecycle creates a window where they diverge:

1. `initiateWithdrawal` — user's rsETH is transferred to `LRTWithdrawalManager`; supply is unchanged.
2. `unlockWithdrawals` (operator) — rsETH is **burned**; supply drops. The corresponding ETH is moved to / stays in `LRTUnstakingVault`.
3. `completeWithdrawal` (user) — ETH leaves `LRTUnstakingVault` and goes to the user.

Between steps 2 and 3, `rsethSupply` is lower but `totalETHInProtocol` is unchanged because `getETHDistributionData` explicitly includes `lrtUnstakingVault.balance`:

```solidity
address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);
ethLyingInUnstakingVault = lrtUnstakingVault.balance;
```

`_getTotalEthInProtocol` sums this via `ILRTDepositPool.getTotalAssetDeposits`, so the ETH committed to withdrawers is still counted as protocol TVL.

When `updateRSETHPrice()` is called in this window:

```solidity
uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);   // uses post-burn supply — understated
// ...
uint256 rewardAmount = totalETHInProtocol - previousTVL; // overstated
protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000; // overstated
// ...
uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);
IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee); // excess minting
```

The protocol mints rsETH to the treasury for "rewards" that are actually just the ETH backing the already-burned rsETH. This dilutes every remaining rsETH holder.

The root cause is structurally identical to the reference report: a **post-update quantity** (`rsethSupply` after burns) is used in a calculation that requires the **pre-update quantity** (supply at the time of the last price snapshot), causing the derived fee to be overstated.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

Every time rsETH is burned (withdrawals unlocked) and `updateRSETHPrice()` is called before the ETH leaves the unstaking vault, the protocol mints excess rsETH to the treasury. This dilutes the value of all outstanding rsETH, effectively transferring yield from depositors to the protocol treasury. The magnitude scales with the amount of rsETH burned and the protocol fee rate.

---

### Likelihood Explanation

**Medium.**

- Withdrawal unlocking is a routine, frequent operation performed by operators.
- `updateRSETHPrice()` is a **public, permissionless** function — any external caller can trigger it immediately after withdrawals are unlocked, maximising the window of exploitation.
- No special privileges or capital are required.

---

### Recommendation

Store the rsETH total supply at the time of each price update in a state variable (e.g., `lastSnapshotSupply`) and use that stored value — not the live supply — when computing `previousTVL`:

```solidity
uint256 previousTVL = lastSnapshotSupply.mulWad(rsETHPrice);
// ... fee logic ...
lastSnapshotSupply = rsethSupply; // update snapshot after fee mint
rsETHPrice = newRsETHPrice;
```

This ensures the baseline TVL and the current supply are always from the same point in time, eliminating the mismatch.

---

### Proof of Concept

**Setup:**
- `rsethSupply = 1 000 rsETH`, `rsETHPrice = 1.0 ETH`, `totalETHInProtocol = 1 000 ETH`
- Protocol fee = 10 %

**Step 1 — Operator unlocks withdrawals (100 rsETH burned):**
- `rsethSupply` → 900 rsETH
- 100 ETH remains in `LRTUnstakingVault` → `totalETHInProtocol` still = 1 000 ETH

**Step 2 — Anyone calls `updateRSETHPrice()`:**

```
previousTVL  = 900 × 1.0  = 900 ETH   ← should be 1 000 ETH
rewardAmount = 1 000 − 900 = 100 ETH  ← should be 0 ETH (no real yield)
protocolFee  = 100 × 10%  = 10 ETH    ← entirely fabricated
newRsETHPrice = (1 000 − 10) / 900 ≈ 1.1 ETH
rsethToMint  = 10 / 1.1 ≈ 9.09 rsETH minted to treasury
```

**Result:** The treasury receives ~9.09 rsETH backed by ETH that belongs to withdrawers. All remaining rsETH holders are diluted by ~1 % with no corresponding yield event. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTOracle.sol (L214-250)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }

        if (highestRsethPrice == 0) {
            highestRsethPrice = rsETHPrice;
        }

        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
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

**File:** contracts/LRTOracle.sol (L298-313)
```text
        // mint protocol fee as rsETH if there's a fee to take
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
        }

        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTOracle.sol (L331-349)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

            unchecked {
                ++assetIdx;
            }
        }
    }
```

**File:** contracts/LRTDepositPool.sol (L494-499)
```text

        address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);
        ethLyingInUnstakingVault = lrtUnstakingVault.balance;

        address lrtConverter = lrtConfig.getContract(LRTConstants.LRT_CONVERTER);
        ethLyingInConverter = ILRTConverter(lrtConverter).ethValueInWithdrawal();
```
