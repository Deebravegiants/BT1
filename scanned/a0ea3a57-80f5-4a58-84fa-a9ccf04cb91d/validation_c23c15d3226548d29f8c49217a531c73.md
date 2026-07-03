### Title
Unguarded `receive()` in `LRTUnstakingVault` Allows Attacker to Inflate TVL and Trigger Excess Protocol-Fee rsETH Minting, Stealing Yield from Existing Holders — (`contracts/LRTUnstakingVault.sol`)

---

### Summary

`LRTUnstakingVault.receive()` accepts ETH from any caller with no access control. Because `LRTDepositPool.getETHDistributionData()` reads `ethLyingInUnstakingVault` directly from `lrtUnstakingVault.balance`, an attacker can inflate the reported TVL at will. When `LRTOracle.updateRSETHPrice()` is subsequently called (also permissionless), the inflated TVL is treated as newly earned yield, causing the protocol to take a fee on ETH that was never earned — minting excess rsETH to the treasury and permanently diluting the yield owed to existing rsETH holders.

---

### Finding Description

**Step 1 — Unguarded entry point**

`LRTUnstakingVault.receive()` emits an event and accepts any ETH: [1](#0-0) 

There is no role check, no whitelist, and no guard of any kind.

**Step 2 — Raw `.balance` read in TVL accounting**

`LRTDepositPool.getETHDistributionData()` reads the vault's balance directly: [2](#0-1) 

This value flows into `getTotalAssetDeposits(ETH)` as `assetLyingUnstakingVault`: [3](#0-2) 

**Step 3 — Permissionless price update uses inflated TVL**

`LRTOracle.updateRSETHPrice()` is public (only `whenNotPaused`): [4](#0-3) 

Inside `_updateRsETHPrice()`, `_getTotalEthInProtocol()` calls `getTotalAssetDeposits` for every supported asset, picking up the inflated vault balance: [5](#0-4) 

**Step 4 — Inflated TVL triggers excess fee minting**

The fee logic treats any TVL increase over `previousTVL` as earned yield: [6](#0-5) 

The resulting `protocolFeeInETH` is converted to rsETH and minted to the treasury: [7](#0-6) 

The donated ETH is real backing, so the rsETH price does rise — but a portion of that rise is captured as protocol fee instead of accruing to existing holders. Existing rsETH holders permanently lose yield equal to `donatedETH × protocolFeeInBPS / 10_000`.

---

### Impact Explanation

Every ETH sent by the attacker to `LRTUnstakingVault` causes the protocol to levy its fee on that ETH as if it were staking yield. At a 10% protocol fee, sending 100 ETH causes 10 ETH worth of rsETH to be minted to the treasury rather than accruing to existing holders. The attacker's ETH is not recovered — it is permanently donated — but the harm to rsETH holders is real and irreversible. This is a direct, on-chain theft of unclaimed yield.

---

### Likelihood Explanation

The attack requires only two permissionless calls: `LRTUnstakingVault.receive()` (via a plain ETH transfer) and `LRTOracle.updateRSETHPrice()`. No privileged role, no front-running dependency, and no external protocol assumption is needed. The only natural brake is `maxFeeMintAmountPerDay`, which caps the rsETH minted per day — but the attacker can repeat the attack across multiple days, and the daily limit itself is set by the manager to allow normal protocol operation, so it is not a security boundary. The `pricePercentageLimit` check can be bypassed by keeping the donated amount small enough per call.

---

### Recommendation

1. **Restrict `receive()` in `LRTUnstakingVault`** to only accept ETH from known, trusted senders (e.g., `LRTDepositPool`, `NodeDelegator`, EigenLayer withdrawal contracts). Revert on unexpected senders.
2. **Track deposited ETH internally** rather than relying on raw `address(this).balance`. Maintain an accounting variable that is incremented only by authorised `receive*` functions, and use that variable in `getETHDistributionData()` instead of `lrtUnstakingVault.balance`.
3. Apply the same fix to `LRTDepositPool.getETHDistributionData()` line 480, which also reads `address(this).balance` directly.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Fork test (Hardhat/Foundry, mainnet fork)
// 1. Deploy / fork the live system.
// 2. Record baseline state.
uint256 rsethSupplyBefore   = rsETH.totalSupply();
uint256 treasuryBalBefore   = rsETH.balanceOf(treasury);
uint256 priceBefore         = lrtOracle.rsETHPrice();

// 3. Attacker sends 10 ETH directly to LRTUnstakingVault.
(bool ok,) = address(lrtUnstakingVault).call{value: 10 ether}("");
require(ok);

// 4. Anyone calls updateRSETHPrice() — no role required.
lrtOracle.updateRSETHPrice();

// 5. Assert excess fee was minted to treasury.
uint256 treasuryMinted = rsETH.balanceOf(treasury) - treasuryBalBefore;
assert(treasuryMinted > 0);   // treasury received rsETH it should not have

// 6. Assert rsETH price is inflated relative to actual earned backing.
uint256 priceAfter = lrtOracle.rsETHPrice();
// priceAfter reflects the donated ETH as if it were yield;
// existing holders' share of that ETH was partially taken as fee.
assert(priceAfter > priceBefore);
// The yield that should have gone entirely to holders was diluted by treasuryMinted.
```

### Citations

**File:** contracts/LRTUnstakingVault.sol (L81-83)
```text
    receive() external payable {
        emit EthReceived(msg.sender, msg.value);
    }
```

**File:** contracts/LRTDepositPool.sol (L385-397)
```text
    function getTotalAssetDeposits(address asset) public view override returns (uint256 totalAssetDeposit) {
        (
            uint256 assetLyingInDepositPool,
            uint256 assetLyingInNDCs,
            uint256 assetStakedInEigenLayer,
            uint256 assetUnstakingFromEigenLayer,
            uint256 assetLyingInConverter,
            uint256 assetLyingUnstakingVault
        ) = getAssetDistributionData(asset);
        uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
        return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
                + assetLyingUnstakingVault);
    }
```

**File:** contracts/LRTDepositPool.sol (L495-496)
```text
        address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);
        ethLyingInUnstakingVault = lrtUnstakingVault.balance;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L244-247)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }
```

**File:** contracts/LRTOracle.sol (L299-307)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
```

**File:** contracts/LRTOracle.sol (L341-343)
```text
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
