### Title
Donation Attack via Direct Token Transfer Inflates TVL and Blocks Deposits — (`contracts/LRTDepositPool.sol`)

---

### Summary

`LRTDepositPool.getAssetDistributionData` and `getETHDistributionData` compute total protocol TVL using raw `IERC20.balanceOf` and `address.balance` calls on the deposit pool, node delegators, and unstaking vault. Because all three contracts accept unrestricted token/ETH transfers, an unprivileged attacker can donate assets directly to any of these contracts, artificially inflating `getTotalAssetDeposits`. When the inflated total exceeds `depositLimitByAsset`, every subsequent `depositAsset` / `depositETH` call reverts with `MaximumDepositLimitReached`, temporarily freezing new deposits until an admin raises the limit.

---

### Finding Description

**Root cause — raw balance reads in TVL accounting**

`getAssetDistributionData` sums three raw balance reads:

```
assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));          // LRTDepositPool
assetLyingInNDCs       += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);  // each NodeDelegator
assetLyingUnstakingVault = IERC20(asset).balanceOf(lrtUnstakingVault);     // LRTUnstakingVault
``` [1](#0-0) 

`getETHDistributionData` does the same for native ETH:

```
ethLyingInDepositPool = address(this).balance;
ethLyingInNDCs       += nodeDelegatorQueue[i].balance;
ethLyingInUnstakingVault = lrtUnstakingVault.balance;
``` [2](#0-1) 

All three target contracts expose unrestricted receive paths:

- `LRTDepositPool`: `receive() external payable { }` [3](#0-2) 
- `NodeDelegator`: `receive() external payable { emit ETHReceived(...); }` [4](#0-3) 
- `LRTUnstakingVault`: `receive() external payable { emit EthReceived(...); }` [5](#0-4) 

**Deposit-limit enforcement uses the inflatable total**

`_checkIfDepositAmountExceedesCurrentLimit` compares the raw `getTotalAssetDeposits` result against `depositLimitByAsset`:

```solidity
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ERC20
return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));           // ETH
``` [6](#0-5) 

`_beforeDeposit` calls this check and reverts with `MaximumDepositLimitReached` if it returns `true`. [7](#0-6) 

**Secondary impact — rsETH price inflation**

`LRTOracle._updateRsETHPrice` calls `ILRTDepositPool.getTotalAssetDeposits` for every supported asset to compute `totalETHInProtocol`, then derives `newRsETHPrice = totalETHInProtocol / rsethSupply`. [8](#0-7) 

A donation inflates `totalETHInProtocol`, raises `newRsETHPrice`, and causes subsequent depositors to receive fewer rsETH tokens per unit of asset deposited (since `rsethAmountToMint = amount * assetPrice / rsETHPrice`). [9](#0-8) 

---

### Impact Explanation

**Primary — Medium: Temporary freezing of funds (deposit functionality)**

An attacker transfers `depositLimitByAsset(asset) − currentTotalAssetDeposits + 1` tokens directly to `LRTDepositPool`. Every subsequent `depositAsset` call for that asset reverts. The freeze persists until an admin increases the deposit limit or an operator moves the donated tokens onward (which still counts toward the limit). No admin key compromise is required; the attacker only needs to hold the donated tokens.

**Secondary — Low: Contract fails to deliver promised returns**

After the donation, calling the public `updateRSETHPrice()` permanently raises the stored `rsETHPrice`. All future depositors receive fewer rsETH tokens than they would have without the donation, even though the ETH-denominated value is unchanged. The donated tokens are absorbed into the protocol TVL with no corresponding rsETH minted to the donor.

---

### Likelihood Explanation

Deposit limits are routinely set close to current TVL to manage concentration risk. When the gap between current TVL and the limit is small, the attack cost is low. The attack requires no special role, no front-running, and no oracle manipulation — only a direct ERC20 transfer or ETH send to a publicly accessible contract.

---

### Recommendation

Replace raw `balanceOf` / `address.balance` reads with internal accounting variables that are incremented only through the official deposit entry points (`depositAsset`, `depositETH`, `transferAssetToNodeDelegator`, etc.) and decremented on withdrawals. This mirrors the `UniswapV2Pair` reserve-tracking pattern and eliminates the donation surface entirely.

---

### Proof of Concept

```
// Assume: depositLimitByAsset(stETH) = 10_000e18
//         getTotalAssetDeposits(stETH) = 9_999e18  (1 stETH gap)

// Step 1 — attacker donates 2 stETH directly to LRTDepositPool
IERC20(stETH).transfer(address(lrtDepositPool), 2e18);

// Step 2 — getTotalAssetDeposits(stETH) now returns 10_001e18 > 10_000e18

// Step 3 — any legitimate user deposit now reverts
lrtDepositPool.depositAsset(stETH, 1e18, 0, "");
// → reverts: MaximumDepositLimitReached

// Step 4 — same attack works for ETH via selfdestruct or direct send
// (address(lrtDepositPool).balance is read raw in getETHDistributionData)
```

The donated tokens are permanently counted in `getTotalAssetDeposits` (they flow to NDCs and EigenLayer if operators act, but remain in the TVL sum), so the deposit limit remains exceeded until an admin raises it.

### Citations

**File:** contracts/LRTDepositPool.sol (L58-58)
```text
    receive() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L444-461)
```text
        assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));

        uint256 ndcsCount = nodeDelegatorQueue.length;
        for (uint256 i; i < ndcsCount;) {
            assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);

            assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
            assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);

            unchecked {
                ++i;
            }
        }

        address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);

        assetLyingInConverter = 0; // assets in converter are accounted in their eth value => getETHDistributionData()
        assetLyingUnstakingVault = IERC20(asset).balanceOf(lrtUnstakingVault);
```

**File:** contracts/LRTDepositPool.sol (L480-496)
```text
        ethLyingInDepositPool = address(this).balance;

        uint256 ndcsCount = nodeDelegatorQueue.length;

        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
            unchecked {
                ++i;
            }
        }

        address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);
        ethLyingInUnstakingVault = lrtUnstakingVault.balance;
```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTDepositPool.sol (L661-663)
```text
        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }
```

**File:** contracts/LRTDepositPool.sol (L676-682)
```text
    function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (asset == LRTConstants.ETH_TOKEN) {
            return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
        }
        return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
    }
```

**File:** contracts/NodeDelegator.sol (L81-83)
```text
    receive() external payable {
        emit ETHReceived(msg.sender, msg.value);
    }
```

**File:** contracts/LRTUnstakingVault.sol (L81-83)
```text
    receive() external payable {
        emit EthReceived(msg.sender, msg.value);
    }
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
