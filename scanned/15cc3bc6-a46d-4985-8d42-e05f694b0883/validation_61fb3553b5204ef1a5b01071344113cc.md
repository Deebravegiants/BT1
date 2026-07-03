### Title
Wrong Variable Used in ETH Deposit Limit Check Allows Deposit Cap Bypass - (File: contracts/LRTDepositPool.sol)

### Summary
In `LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit`, the ETH branch omits the incoming `amount` from the limit comparison. Any unprivileged depositor can call `depositETH()` and deposit an arbitrarily large amount of ETH as long as the current total has not already crossed the cap, completely bypassing the governance-set deposit limit.

### Finding Description
The internal function `_checkIfDepositAmountExceedesCurrentLimit` contains two branches: one for ETH and one for ERC-20 tokens.

```solidity
// contracts/LRTDepositPool.sol  lines 676-682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount ignored
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct
}
```

The ERC-20 branch correctly evaluates `totalAssetDeposits + amount > limit`. The ETH branch evaluates only `totalAssetDeposits > limit`, silently discarding the `amount` parameter. This is the direct analog of the external report: the wrong value is used in the validation condition.

Because `_beforeDeposit` calls this function and reverts only when it returns `true`, the ETH deposit limit is never triggered by the incoming deposit amount — only by the pre-existing total. A depositor can therefore push the protocol's ETH holdings arbitrarily above the governance-set cap in a single transaction. [1](#0-0) 

The public entry point is `depositETH`, which is callable by any address with no role restriction: [2](#0-1) 

`_beforeDeposit` is the only guard between the caller and the mint: [3](#0-2) 

### Impact Explanation
The ETH deposit limit is a governance-controlled risk parameter that bounds the protocol's EigenLayer exposure. Bypassing it allows the protocol to restake more ETH than governance intended. If EigenLayer slashing occurs on the excess stake, rsETH holders bear losses that the deposit cap was designed to prevent. The bypass is silent — no event or revert signals that the limit has been exceeded — so the protocol operates outside its intended risk envelope without any on-chain indication.

**Impact: Medium — temporary or permanent over-exposure to EigenLayer slashing risk; contract fails to enforce its promised deposit ceiling.**

### Likelihood Explanation
The entry point `depositETH` is public and payable with no role restriction. Any depositor who observes that `totalAssetDeposits` is below the limit can immediately exploit the gap. No special conditions, timing, or privileged access are required. Likelihood is **High**.

### Recommendation
Add `amount` to the ETH branch, matching the ERC-20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

### Proof of Concept
1. Governance sets `depositLimitByAsset(ETH_TOKEN) = 1000 ether`.
2. Current `getTotalAssetDeposits(ETH_TOKEN)` returns `999 ether`.
3. Attacker calls `depositETH{value: 10_000 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit` evaluates `999 ether > 1000 ether` → `false`.
5. `_beforeDeposit` does not revert; `10_000 ether` worth of rsETH is minted.
6. Protocol now holds `10_999 ether` of ETH under EigenLayer management, 10× the intended cap. [1](#0-0)

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
