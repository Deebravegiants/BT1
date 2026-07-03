### Title
ETH Deposit Limit Bypass via Incorrect Bounds Check in `_checkIfDepositAmountExceedesCurrentLimit` - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` applies two structurally different checks depending on the asset type. For non-ETH tokens it correctly tests `totalAssetDeposits + amount > depositLimit`, but for ETH it tests only `totalAssetDeposits > depositLimit`, omitting the incoming deposit amount entirely. This is the Solidity analog of the zkasm off-by-one: the boundary value passes through when it should be blocked, allowing any depositor to push ETH holdings arbitrarily above the configured cap in a single transaction.

### Finding Description
`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` (lines 676–682) contains a branching bounds check:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← missing + amount
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [1](#0-0) 

For ETH the function returns `true` (i.e., "limit exceeded, revert") only when the pre-deposit total already exceeds the cap. It never considers the size of the incoming deposit. Consequently, whenever `totalAssetDeposits < depositLimit`, the check returns `false` regardless of `amount`, and `depositETH` proceeds to mint rsETH for the full `msg.value`.

The non-ETH branch correctly adds `amount` before comparing, so the asymmetry is a clear implementation defect in the ETH path. [2](#0-1) 

### Impact Explanation
When the admin has configured a non-zero ETH deposit limit (the normal production state), any unprivileged depositor can:

1. Observe `totalAssetDeposits < depositLimit`.
2. Call `depositETH` with an arbitrarily large `msg.value`.
3. The check passes (`totalAssetDeposits > depositLimit` is false), rsETH is minted for the full amount, and the ETH total is pushed far above the cap.

The deposit limit exists to bound EigenLayer strategy exposure and control rsETH supply growth. Bypassing it causes rsETH to be minted against ETH that cannot be deployed into EigenLayer strategies (which have their own capacity limits), meaning those rsETH holders receive a token backed by idle, non-yield-bearing ETH. This matches the **Low – Contract fails to deliver promised returns** impact tier; it can escalate to **Medium – Temporary freezing of funds** if the excess ETH cannot be routed to any NodeDelegator strategy and becomes stranded in the pool.

### Likelihood Explanation
The entry point `depositETH` is public and payable with no role restriction. [3](#0-2) 

The only precondition is that the admin has set a non-zero `depositLimitByAsset` for ETH, which is the expected production configuration whenever a cap is desired. No privileged access, oracle manipulation, or front-running is required. Any depositor who monitors the on-chain state can trigger this in a single transaction.

### Recommendation
Replace the ETH branch with the same `+ amount` pattern used for ERC-20 tokens:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

This makes the ETH and non-ETH paths consistent and ensures the incoming deposit amount is always included in the limit comparison before minting rsETH.

### Proof of Concept
Assume `depositLimitByAsset[ETH_TOKEN] = 100 ether` and `getTotalAssetDeposits(ETH_TOKEN) = 50 ether`.

1. Attacker calls `depositETH{value: 1000 ether}("")`.
2. `_beforeDeposit` calls `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 1000 ether)`.
3. ETH branch evaluates `50 ether > 100 ether` → `false` → limit not exceeded.
4. `getRsETHAmountToMint` computes rsETH for 1000 ETH; `_mintRsETH` mints it to the attacker.
5. Post-deposit: `getTotalAssetDeposits(ETH_TOKEN) = 1050 ether`, 950 ETH above the configured cap.
6. The same call with a non-ETH token of equal value would have evaluated `50 + 1000 > 100` → `true` → revert, demonstrating the asymmetry. [1](#0-0) [4](#0-3)

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
