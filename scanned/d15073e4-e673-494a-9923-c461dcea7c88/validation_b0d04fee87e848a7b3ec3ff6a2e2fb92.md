### Title
Donation to `LRTDepositPool` Inflates `rsETHPrice`, Causing Depositors to Receive Fewer rsETH Tokens - (File: contracts/LRTDepositPool.sol)

---

### Summary

`LRTDepositPool.getAssetDistributionData()` and `getETHDistributionData()` measure protocol-held assets using raw `IERC20(asset).balanceOf(address(this))` and `address(this).balance`. These values feed directly into `getTotalAssetDeposits()` → `LRTOracle._getTotalEthInProtocol()` → `_updateRsETHPrice()`. Because `updateRSETHPrice()` is a public, permissionless function, any attacker can donate tokens or ETH to the deposit pool and then call `updateRSETHPrice()` to permanently inflate the stored `rsETHPrice`. Subsequent depositors then receive fewer rsETH tokens than they are entitled to.

---

### Finding Description

`LRTDepositPool.getAssetDistributionData()` computes the deposit pool's share of total protocol assets as:

```solidity
assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
``` [1](#0-0) 

Similarly, `getETHDistributionData()` uses:

```solidity
ethLyingInDepositPool = address(this).balance;
``` [2](#0-1) 

Both values are aggregated by `getTotalAssetDeposits()`: [3](#0-2) 

`LRTOracle._getTotalEthInProtocol()` calls `getTotalAssetDeposits()` for every supported asset and sums the ETH-denominated value: [4](#0-3) 

This total is then used to compute the new rsETH price:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [5](#0-4) 

The stored `rsETHPrice` is updated by `updateRSETHPrice()`, which is **public and callable by anyone**: [6](#0-5) 

The stored `rsETHPrice` is then used in `getRsETHAmountToMint()` to determine how many rsETH tokens a depositor receives:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [7](#0-6) 

A higher `rsETHPrice` denominator means fewer rsETH minted per unit of deposited asset.

The `LRTDepositPool` has an open `receive()` function accepting ETH: [8](#0-7) 

---

### Impact Explanation

An attacker who donates LST tokens or ETH directly to `LRTDepositPool` and then calls the public `updateRSETHPrice()` permanently inflates the stored `rsETHPrice`. All subsequent depositors calling `depositAsset()` or `depositETH()` receive fewer rsETH tokens than they are entitled to for their deposit. The inflated `highestRsethPrice` is also permanently recorded, meaning the price floor for downside-protection pausing is raised, which can cause the protocol to pause prematurely on any future price correction.

**Impact:** Low — contract fails to deliver promised returns (depositors receive fewer rsETH than they should).

---

### Likelihood Explanation

The attack requires only two permissionless transactions: a direct token/ETH transfer to `LRTDepositPool` and a call to `updateRSETHPrice()`. No privileged role is needed. The cost to the attacker is the donated amount, making large-scale manipulation expensive but small griefing attacks cheap. The attack is realistic for any motivated actor wishing to harm depositors or raise the `highestRsethPrice` ceiling.

---

### Recommendation

Replace raw `balanceOf(address(this))` and `address(this).balance` in `getAssetDistributionData()` and `getETHDistributionData()` with an internal accounting variable (e.g., a `depositedAmount` mapping) that is incremented only on verified deposits via `depositAsset()` / `depositETH()` and decremented on verified outflows (transfers to NodeDelegators, UnstakingVault, etc.). This prevents untracked donations from inflating the TVL used in price computation.

---

### Proof of Concept

```solidity
// Attacker inflates rsETHPrice by donating rsETH-supported LST to LRTDepositPool

function testDonationInflatesRsETHPrice() public {
    // Record rsETHPrice before attack
    uint256 priceBefore = lrtOracle.rsETHPrice();

    // Attacker sends stETH directly to LRTDepositPool (no deposit, no rsETH minted)
    vm.startPrank(attacker);
    stETH.transfer(address(lrtDepositPool), 10 ether);

    // Anyone can call updateRSETHPrice — it is public
    lrtOracle.updateRSETHPrice();
    vm.stopPrank();

    uint256 priceAfter = lrtOracle.rsETHPrice();
    // rsETHPrice is now higher than before the donation
    assertGt(priceAfter, priceBefore);

    // Victim deposits 1 ether of stETH — receives fewer rsETH than expected
    vm.startPrank(victim);
    stETH.approve(address(lrtDepositPool), 1 ether);
    uint256 rsETHMinted = lrtDepositPool.depositAsset(address(stETH), 1 ether, 0, "");
    vm.stopPrank();

    // rsETHMinted is less than it would have been without the donation
    uint256 fairAmount = (1 ether * lrtOracle.getAssetPrice(address(stETH))) / priceBefore;
    assertLt(rsETHMinted, fairAmount);
}
```

### Citations

**File:** contracts/LRTDepositPool.sol (L58-58)
```text
    receive() external payable { }
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

**File:** contracts/LRTDepositPool.sol (L444-444)
```text
        assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
```

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L341-343)
```text
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
