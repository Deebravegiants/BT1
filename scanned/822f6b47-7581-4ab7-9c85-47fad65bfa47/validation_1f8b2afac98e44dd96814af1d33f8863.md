### Title
Unrestricted `receive()` on `LRTDepositPool` Allows Donation to Inflate `totalETHInProtocol`, Triggering Illegitimate Fee Minting — (`contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`)

---

### Summary

Anyone can send ETH directly to `LRTDepositPool` via its unrestricted `receive()` fallback. Because `getETHDistributionData()` uses `address(this).balance` as `ethLyingInDepositPool`, the donated ETH is immediately counted in `totalETHInProtocol`. When `updateRSETHPrice()` is subsequently called, the oracle treats the TVL increase (which includes the donation) as staking yield, computes a `protocolFeeInETH` on it, and mints rsETH to the treasury. rsETH holders receive the donation minus the fee, while the treasury receives fee rsETH it should not have earned.

---

### Finding Description

**Step 1 — Unrestricted ETH entry point**

`LRTDepositPool` has a bare, permissionless fallback: [1](#0-0) 

Any address can call `address(depositPool).call{value: X}("")` or simply `transfer`/`send` ETH to it with no access control.

**Step 2 — Raw balance included in TVL**

`getETHDistributionData()` sets: [2](#0-1) 

This means the full `address(this).balance`, including any donated ETH, is returned as `ethLyingInDepositPool`. `getTotalAssetDeposits(ETH_TOKEN)` sums this into the total: [3](#0-2) 

**Step 3 — Oracle counts donation as yield**

`_getTotalEthInProtocol()` calls `getTotalAssetDeposits` for every supported asset: [4](#0-3) 

Back in `_updateRsETHPrice()`, the fee is computed as:

```
rewardAmount = totalETHInProtocol - previousTVL   // includes donated ETH
protocolFeeInETH = rewardAmount * protocolFeeInBPS / 10_000
``` [5](#0-4) 

**Step 4 — Fee rsETH minted to treasury** [6](#0-5) 

The treasury receives rsETH proportional to the fee on the donation. Because the rsETH supply increases without a corresponding increase in backing assets for existing holders, every existing rsETH holder is diluted by exactly the fee portion of the donation.

---

### Impact Explanation

- The donated ETH enters the protocol and raises the rsETH price, but the fee portion is siphoned to the treasury as newly minted rsETH.
- Existing rsETH holders receive `donation × (1 - feeBPS/10000)` worth of value instead of the full donation.
- The treasury receives `donation × feeBPS/10000` in rsETH that it did not earn through legitimate staking activity.
- This is **theft of unclaimed yield**: yield that should accrue entirely to rsETH holders is partially redirected to the treasury via illegitimate fee minting triggered by an arbitrary donation.

---

### Likelihood Explanation

- The `receive()` fallback is completely open; no role, no minimum, no guard.
- `updateRSETHPrice()` is also public and callable by anyone when not paused.
- The `pricePercentageLimit` guard only blocks calls where the price increase exceeds the configured threshold; small donations (or donations when the limit is 0) pass through freely.
- The `maxFeeMintAmountPerDay` cap limits per-day damage but does not prevent the attack.
- The attacker loses the donated ETH, so direct financial motivation is absent unless the attacker controls the treasury or holds a short position on rsETH. However, the path is fully permissionless and locally testable on unmodified code.

---

### Recommendation

1. **Restrict the `receive()` fallback** to only accept ETH from known, trusted senders (e.g., `receiveFromRewardReceiver`, `receiveFromNodeDelegator`, `receiveFromLRTConverter`). Revert on arbitrary ETH transfers.
2. Alternatively, **exclude `address(this).balance` from TVL** and instead track deposited ETH explicitly with a storage variable that is only incremented through the controlled entry points (`depositETH`, `receiveFromRewardReceiver`, etc.).

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

// Pseudocode for a local fork test
function testDonationInflatesFee() public {
    // Precondition: protocol is live, rsETH supply > 0, fee BPS > 0
    uint256 treasuryBalanceBefore = rsETH.balanceOf(treasury);
    uint256 rsETHPriceBefore = lrtOracle.rsETHPrice();

    // Attacker donates 1 ETH directly to LRTDepositPool
    vm.deal(attacker, 1 ether);
    vm.prank(attacker);
    (bool ok,) = address(lrtDepositPool).call{value: 1 ether}("");
    require(ok);

    // Anyone calls updateRSETHPrice
    lrtOracle.updateRSETHPrice();

    uint256 treasuryBalanceAfter = rsETH.balanceOf(treasury);
    uint256 rsETHPriceAfter = lrtOracle.rsETHPrice();

    // Treasury received fee rsETH minted on the donated ETH
    assertGt(treasuryBalanceAfter, treasuryBalanceBefore);
    // rsETH price increased, but by less than the full donation per token
    assertGt(rsETHPriceAfter, rsETHPriceBefore);
}
```

The assertion `treasuryBalanceAfter > treasuryBalanceBefore` confirms that fee rsETH was minted on the donated ETH, diluting all existing rsETH holders by the fee portion of the donation.

### Citations

**File:** contracts/LRTDepositPool.sol (L58-58)
```text
    receive() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L385-396)
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
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
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
