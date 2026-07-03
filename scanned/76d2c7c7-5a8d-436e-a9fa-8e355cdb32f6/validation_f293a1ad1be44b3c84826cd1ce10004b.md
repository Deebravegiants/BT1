### Title
ETH Deposit Limit Not Enforced Correctly Due to Missing Amount in Boundary Check - (File: contracts/LRTDepositPool.sol)

### Summary
`_checkIfDepositAmountExceedesCurrentLimit` applies an inconsistent check for ETH versus ERC-20 assets. The ETH branch omits the incoming deposit `amount` from the comparison, so a depositor can push the total ETH held by the protocol above the configured cap in a single transaction.

### Finding Description
`_checkIfDepositAmountExceedesCurrentLimit` is the sole gate that enforces the per-asset deposit cap before rsETH is minted:

```solidity
// contracts/LRTDepositPool.sol  lines 676-682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount NOT added
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← amount IS added
}
```

For every ERC-20 asset the check is `totalAssetDeposits + amount > limit`, which correctly rejects a deposit that would breach the cap. For ETH the check is only `totalAssetDeposits > limit`, which returns `false` (i.e. "not exceeded") whenever `totalAssetDeposits == limit`. A caller who sends any non-zero ETH at that moment will pass the gate, mint rsETH, and leave `totalAssetDeposits` above the limit. The function name and the ERC-20 branch both express the intent to include the incoming amount; the ETH branch silently omits it — a direct copy-paste / inconsistency error analogous to the wrong-variable-in-validation pattern in the reference report.

The caller path is fully unprivileged:

```
depositETH(minRSETHAmountExpected, referralId)   // payable, no role check
  → _beforeDeposit(ETH_TOKEN, msg.value, ...)
      → _checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, msg.value)  // returns false when total == limit
  → _mintRsETH(rsethAmountToMint)                // mints rsETH above cap
``` [1](#0-0) [2](#0-1) [3](#0-2) 

### Impact Explanation
The deposit cap is the protocol's primary mechanism for bounding ETH exposure per asset. When the cap is exactly reached, any subsequent ETH deposit still passes the check, mints rsETH, and inflates `totalAssetDeposits` beyond the intended ceiling. This means the protocol delivers more rsETH than the governance-approved limit permits — a failure to honour the promised constraint. Classified as **Low**: contract fails to deliver promised returns (the deposit cap guarantee), but no direct loss of user funds occurs.

### Likelihood Explanation
The condition is trivially reachable by any depositor: watch for `totalAssetDeposits == depositLimit` (or simply be the depositor whose transaction tips the total to exactly the limit) and send any ETH. No special role, front-running advantage, or external dependency is required.

### Recommendation
Add the incoming `amount` to the ETH branch, mirroring the ERC-20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

### Proof of Concept
1. Assume `depositLimitByAsset(ETH_TOKEN) = 1000 ether` and `getTotalAssetDeposits(ETH_TOKEN) = 1000 ether` (cap exactly reached).
2. Alice calls `depositETH{value: 1 ether}(0, "")`.
3. `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 1 ether)` evaluates `1000 ether > 1000 ether` → `false` → no revert.
4. `_mintRsETH` mints rsETH for Alice.
5. `getTotalAssetDeposits(ETH_TOKEN)` is now `1001 ether`, exceeding the cap by `1 ether`.
6. The same step can be repeated by any depositor until the cap is meaningfully exceeded. [1](#0-0)

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
