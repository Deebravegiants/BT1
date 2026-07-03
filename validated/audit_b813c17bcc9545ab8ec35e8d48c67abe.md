### Title
ETH Deposit Limit Check Omits `amount`, Allowing Deposit Cap Bypass — (`contracts/LRTDepositPool.sol`)

### Summary
`_checkIfDepositAmountExceedesCurrentLimit()` applies an asymmetric validation: for ERC-20 assets it correctly tests `totalAssetDeposits + amount > depositLimit`, but for ETH it tests only `totalAssetDeposits > depositLimit`, omitting the incoming `amount`. Any depositor can therefore push the ETH TVL arbitrarily above the configured cap in a single call, directly analogous to the PoolTogether finding where `maxDeposit` was checked but `maxMint` was not.

### Finding Description
`_beforeDeposit()` delegates the cap check to `_checkIfDepositAmountExceedesCurrentLimit()`:

```solidity
// LRTDepositPool.sol  _checkIfDepositAmountExceedesCurrentLimit
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount absent
}
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct for ERC-20
```

The ETH branch asks "has the limit already been exceeded?" rather than "would this deposit exceed the limit?". As long as `totalAssetDeposits ≤ depositLimit` at the moment of the call, the check returns `false` regardless of how large `amount` is, and the deposit proceeds. The ERC-20 branch correctly includes `amount` in the comparison.

`getAssetCurrentLimit()` (the public view helper) computes the remaining headroom correctly for all assets, making the inconsistency in the internal check clearly unintentional.

### Impact Explanation
The ETH deposit cap is the protocol's primary TVL risk-management control for native ETH. Bypassing it allows a single depositor to push the ETH balance far beyond the intended ceiling in one transaction. Excess ETH is immediately eligible to be forwarded to NodeDelegators and staked into EigenLayer, expanding protocol exposure beyond what governance has approved. If the cap was set to bound insolvency risk (e.g., while EigenLayer withdrawal queues are long), the bypass can directly contribute to protocol insolvency. At minimum it permanently violates the invariant that `getTotalAssetDeposits(ETH) ≤ depositLimitByAsset(ETH)`, breaking any off-chain or on-chain logic that relies on that invariant.

**Impact: Medium — temporary/permanent freezing of unclaimed yield and potential protocol insolvency path.**

### Likelihood Explanation
No special role, flash loan, or oracle manipulation is required. Any unprivileged user calling `depositETH()` while `totalAssetDeposits < depositLimit` can supply an arbitrarily large `msg.value`. The condition is trivially reachable at any point before the cap is already breached.

### Recommendation
Add `amount` to the ETH branch, mirroring the ERC-20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

### Proof of Concept
1. Admin sets `depositLimitByAsset(ETH_TOKEN) = 1 000 ETH`.
2. Current `getTotalAssetDeposits(ETH_TOKEN) = 999 ETH`.
3. Attacker calls `depositETH{value: 5 000 ETH}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit` evaluates `999 > 1 000` → `false` → no revert.
5. `_mintRsETH` mints rsETH for 5 000 ETH; total ETH in protocol becomes 5 999 ETH — nearly 6× the intended cap.
6. The excess ETH is forwarded to NodeDelegators and staked into EigenLayer, permanently expanding protocol exposure beyond the governance-approved limit. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** contracts/LRTDepositPool.sol (L402-409)
```text
    function getAssetCurrentLimit(address asset) public view override returns (uint256) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)) {
            return 0;
        }

        return lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;
    }
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
