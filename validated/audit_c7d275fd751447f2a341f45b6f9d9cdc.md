### Title
Token Donation Inflates `balanceOf()`-Based TVL, Enabling rsETH Price Manipulation and Fund Theft - (File: contracts/LRTOracle.sol, contracts/LRTDepositPool.sol)

---

### Summary

`LRTDepositPool.getAssetDistributionData()` measures protocol TVL using raw `IERC20(asset).balanceOf()` calls on the deposit pool, node delegators, and unstaking vault. Because `LRTOracle.updateRSETHPrice()` is a permissionless public function that recomputes `rsETHPrice` from this TVL, any attacker can donate supported LST tokens directly to those contracts, call `updateRSETHPrice()`, and inflate the stored `rsETHPrice`. The inflated price is then used verbatim by `LRTWithdrawalManager.getExpectedAssetAmount()` to determine how many LST tokens a user receives per rsETH burned, enabling the attacker to drain protocol assets.

---

### Finding Description

**Step 1 – TVL is measured with raw `balanceOf()`**

`LRTDepositPool.getAssetDistributionData()` computes the total asset amount held by the protocol using three live `balanceOf()` reads:

```solidity
assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));          // line 444
assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);        // line 448
assetLyingUnstakingVault = IERC20(asset).balanceOf(lrtUnstakingVault);     // line 461
``` [1](#0-0) 

`getTotalAssetDeposits()` sums these values and returns the total. [2](#0-1) 

**Step 2 – rsETH price is derived from this TVL**

`LRTOracle._getTotalEthInProtocol()` calls `getTotalAssetDeposits()` for every supported asset and multiplies by the asset's oracle price:

```solidity
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
``` [3](#0-2) 

`_updateRsETHPrice()` then sets:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [4](#0-3) 

**Step 3 – `updateRSETHPrice()` is permissionless**

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [5](#0-4) 

Any external caller can trigger a price update at any time.

**Step 4 – Withdrawal amount is computed from the stored `rsETHPrice`**

`LRTWithdrawalManager.getExpectedAssetAmount()` reads the stored price directly:

```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
``` [6](#0-5) 

This value is locked in at `initiateWithdrawal()` time as `expectedAssetAmount` and paid out at `completeWithdrawal()` / `instantWithdrawal()`. [7](#0-6) 

---

### Impact Explanation

**Critical – Direct theft of user funds.**

An attacker who inflates `rsETHPrice` by donating tokens receives more LST per rsETH burned than the protocol actually holds on their behalf. The excess comes from other depositors' assets, constituting direct theft. With `pricePercentageLimit == 0` (the default/unset state), a single large donation can inflate the price arbitrarily. Even with a non-zero limit, the attacker can repeat the attack across multiple oracle update cycles to gradually drain the protocol.

---

### Likelihood Explanation

**Medium.** The attack requires:
1. Holding or flash-borrowing rsETH (widely available on-chain).
2. Donating a supported LST (stETH, ETHx) to `LRTDepositPool` or any registered NDC or `LRTUnstakingVault` — a plain ERC-20 transfer, no special access.
3. Calling the public `updateRSETHPrice()`.
4. Calling `instantWithdrawal()` (if enabled) or `initiateWithdrawal()`.

No privileged role is required. The attack is fully executable by any external account. The `pricePercentageLimit` guard is a partial mitigation only when explicitly configured by the admin; it is `0` by default.

---

### Recommendation

1. **Use internal accounting instead of `balanceOf()`**: Track deposited amounts in storage variables that are incremented/decremented only through controlled protocol entry points (`depositAsset`, `transferAssetToNodeDelegator`, etc.). Do not count arbitrary token balances held by protocol contracts.

2. **Restrict `updateRSETHPrice()` to authorized callers** (e.g., a keeper role or the manager role) so that an attacker cannot trigger a price update immediately after a donation.

3. **Enforce `pricePercentageLimit > 0` as a deployment invariant** and ensure it is set before the protocol goes live.

---

### Proof of Concept

```
// Attacker setup: holds 1 rsETH (acquired legitimately or via flash loan)

// Step 1: Donate 10,000 stETH directly to LRTDepositPool
stETH.transfer(address(lrtDepositPool), 10_000e18);

// Step 2: Trigger permissionless price update
// LRTOracle._getTotalEthInProtocol() now reads the inflated balanceOf()
// rsETHPrice = (old_TVL + 10_000 ETH_equivalent) / rsethSupply  →  massively inflated
lrtOracle.updateRSETHPrice();

// Step 3: Initiate withdrawal with 1 rsETH
// getExpectedAssetAmount(stETH, 1e18) = 1e18 * inflatedRsETHPrice / stETHPrice
// Returns far more stETH than 1 rsETH is worth
lrtWithdrawalManager.initiateWithdrawal(stETH, 1e18, "");

// (wait for delay or use instantWithdrawal if enabled)
// Step 4: Collect inflated stETH payout — protocol drained
lrtWithdrawalManager.completeWithdrawal(stETH, "");
```

The donated stETH is also counted in `getAvailableAssetAmount()` (which calls `getTotalAssetDeposits()`), so the `ExceedAmountToWithdraw` guard at line 170 does not block the inflated withdrawal request. [8](#0-7) [9](#0-8)

### Citations

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

**File:** contracts/LRTWithdrawalManager.sol (L168-175)
```text
        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L593-593)
```text
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

**File:** contracts/LRTWithdrawalManager.sol (L599-602)
```text
    function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
```
