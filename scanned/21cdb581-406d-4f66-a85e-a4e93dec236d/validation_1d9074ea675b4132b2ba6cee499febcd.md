### Title
ETH Deposit Limit Check Omits Deposit Amount, Allowing Limit Bypass - (File: contracts/LRTDepositPool.sol)

### Summary
In `LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit`, the ETH branch of the deposit-cap check omits the incoming `amount` from the comparison. Unlike the ERC20 branch, which correctly tests `totalAssetDeposits + amount > depositLimit`, the ETH branch only tests `totalAssetDeposits > depositLimit`. Any unprivileged depositor can therefore push the protocol's ETH holdings above the admin-configured cap in a single `depositETH` call.

### Finding Description
`_checkIfDepositAmountExceedesCurrentLimit` is the sole gate that enforces the per-asset deposit limit before rsETH is minted:

```solidity
// contracts/LRTDepositPool.sol  lines 676-682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount missing
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct
}
``` [1](#0-0) 

The ETH branch evaluates whether the limit has **already been exceeded** before the deposit, not whether the deposit **would exceed** it. The ERC20 branch correctly adds `amount` to `totalAssetDeposits` before comparing. This is the same class of inverted/incorrect comparison described in the external report: the condition passes (returns `false`) precisely when it should fail (return `true`), and the caller reverts only when the limit was already breached.

The result is used directly in `_beforeDeposit`:

```solidity
// contracts/LRTDepositPool.sol  lines 661-663
if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
    revert MaximumDepositLimitReached();
}
``` [2](#0-1) 

which is called by the public `depositETH` entry point:

```solidity
// contracts/LRTDepositPool.sol  lines 76-93
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId)
    external payable nonReentrant whenNotPaused onlySupportedAsset(LRTConstants.ETH_TOKEN)
{
    uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);
    _mintRsETH(rsethAmountToMint);
    emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
}
``` [3](#0-2) 

### Impact Explanation
The deposit limit is the protocol's primary mechanism for capping ETH exposure (e.g., to bound EigenLayer strategy risk or total TVL). Because the ETH check never includes the incoming deposit amount, a single large deposit can push the on-chain ETH total arbitrarily above the configured cap. The protocol will hold and restake more ETH than the admin intended, violating the promised deposit ceiling. This maps to **Low — contract fails to deliver promised returns** (the deposit limit guarantee is broken for ETH). If the limit was set to bound EigenLayer strategy capacity, excess deposits could also cause downstream operational failures, elevating the impact to **Medium — temporary freezing of funds**.

### Likelihood Explanation
The entry path is fully permissionless: any address can call `depositETH` with `msg.value > 0`. No special role, front-running, or external dependency is required. The condition is triggered whenever `totalAssetDeposits ≤ depositLimit` and `totalAssetDeposits + depositAmount > depositLimit`, which is the normal boundary condition the limit is designed to enforce. Likelihood is **High**.

### Recommendation
Add `amount` to the ETH branch, matching the ERC20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

### Proof of Concept
1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 100 ether`.
2. Current `getTotalAssetDeposits(ETH_TOKEN)` returns `99 ether`.
3. Attacker calls `depositETH{value: 10 ether}(0, "")`.
4. Inside `_checkIfDepositAmountExceedesCurrentLimit`: `99 ether > 100 ether` → `false` → no revert.
5. `_mintRsETH` executes; total ETH in protocol becomes `109 ether`, exceeding the cap by `9 ether`.
6. For comparison, an ERC20 deposit of the same size at the same state would correctly revert: `99 ether + 10 ether > 100 ether` → `true` → `MaximumDepositLimitReached`.

### Citations

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
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
