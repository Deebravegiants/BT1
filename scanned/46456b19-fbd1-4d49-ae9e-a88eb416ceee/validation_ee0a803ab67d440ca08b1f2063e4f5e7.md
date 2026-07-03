### Title
Unprivileged ETH Donation to `LRTDepositPool` Inflates Tracked Balance and Freezes ETH Deposits - (File: contracts/LRTDepositPool.sol)

### Summary
Any external caller can send ETH directly to `LRTDepositPool` via its open `receive()` function. Because `getETHDistributionData()` uses the raw `address(this).balance` as the canonical measure of ETH held in the pool, this donated ETH is indistinguishable from legitimately deposited ETH. The deposit-limit guard for ETH compares this inflated balance against the configured cap, causing all subsequent `depositETH()` calls to revert with `MaximumDepositLimitReached`.

### Finding Description

`LRTDepositPool` exposes an unrestricted `receive()` fallback:

```solidity
receive() external payable { }
``` [1](#0-0) 

`getETHDistributionData()` reports the pool's ETH holding as the raw contract balance:

```solidity
ethLyingInDepositPool = address(this).balance;
``` [2](#0-1) 

`getTotalAssetDeposits()` aggregates this value (plus NDC and EigenLayer balances) into the total ETH figure used for limit enforcement: [3](#0-2) 

The deposit-limit check for ETH is:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
}
``` [4](#0-3) 

Because `depositETH()` is `payable`, the incoming `msg.value` is already reflected in `address(this).balance` before `_beforeDeposit` runs, so the check intentionally omits adding `amount` again. However, this same design means ETH sent directly via `receive()` is also silently counted, with no way to distinguish it from protocol deposits.

### Impact Explanation

An attacker who sends a small amount of ETH directly to `LRTDepositPool` — just enough to push `address(this).balance` to or above `depositLimitByAsset(ETH)` — causes every subsequent `depositETH()` call to revert. The `_beforeDeposit` check fires before any rsETH is minted, so no user can deposit ETH until the operator manually moves the excess ETH to a NodeDelegator (reducing `address(this).balance`). This constitutes a **temporary freezing of ETH deposits** (Medium severity per scope).

### Likelihood Explanation

The attack requires only a direct ETH transfer, callable by any EOA or contract with no special role. The cost to the attacker equals the ETH donated (which is not recoverable by the attacker but is not destroyed — it remains in the protocol). If the deposit limit is nearly full, even a 1 wei donation suffices. The attack can be repeated each time the operator drains the pool to a node delegator.

### Recommendation

Replace the raw `address(this).balance` accounting with an internal ledger variable that is incremented only through the authorised deposit paths (`depositETH`, `receiveFromRewardReceiver`, `receiveFromLRTConverter`, `receiveFromNodeDelegator`). Alternatively, restrict `receive()` to known callers (reward receiver, converter, node delegators) and revert on unexpected senders.

### Proof of Concept

1. Protocol is live; ETH deposit limit is 1 000 ETH; current `address(this).balance` is 999 ETH.
2. Eve calls `LRTDepositPool.receive()` (plain ETH transfer) sending 1 ETH. `address(this).balance` becomes 1 000 ETH.
3. Alice calls `depositETH{value: 1 ether}(minRSETH, "")`.
   - `msg.value` is received → `address(this).balance = 1 001 ETH`.
   - `getTotalAssetDeposits(ETH)` returns 1 001 ETH.
   - `_checkIfDepositAmountExceedesCurrentLimit`: `1001 > 1000` → `true`.
   - Transaction reverts: `MaximumDepositLimitReached`.
4. All ETH deposits are frozen until an operator calls `transferETHToNodeDelegator`, reducing `address(this).balance` below the limit. [5](#0-4) [6](#0-5)

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

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
```

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
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
