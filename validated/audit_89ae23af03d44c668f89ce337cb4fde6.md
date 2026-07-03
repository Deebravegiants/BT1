### Title
ETH Deposit Limit Check Omits Incoming Amount, Allowing One-Deposit Overshoot - (File: contracts/LRTDepositPool.sol)

### Summary
`_checkIfDepositAmountExceedesCurrentLimit` applies an asymmetric check: for ERC-20 assets it tests `totalDeposits + amount > limit`, but for ETH it only tests `totalDeposits > limit`, silently omitting the incoming `amount`. Any depositor can therefore push the ETH TVL above the configured cap by exactly one deposit.

### Finding Description
In `LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit`, the ETH branch and the ERC-20 branch diverge:

```solidity
// LRTDepositPool.sol lines 676-682
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount NOT included
}
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← amount included
```

When `totalAssetDeposits == depositLimit` the ETH branch evaluates `depositLimit > depositLimit` → `false`, so `_beforeDeposit` does not revert and the deposit is accepted. After `depositETH` completes, `totalAssetDeposits` becomes `depositLimit + msg.value`, exceeding the cap. The identical scenario for any ERC-20 token would evaluate `depositLimit + amount > depositLimit` → `true` and revert with `MaximumDepositLimitReached`.

The call chain is:
`depositETH` → `_beforeDeposit` → `_checkIfDepositAmountExceedesCurrentLimit` [1](#0-0) 

The ETH deposit entry point that reaches this check: [2](#0-1) 

The internal `_beforeDeposit` that calls the check: [3](#0-2) 

### Impact Explanation
The deposit limit is a risk-management control set by the admin to cap protocol ETH exposure (e.g., to limit EigenLayer slashing exposure or liquidity risk). The missing `amount` term means the limit can be overshot by up to one full deposit. No funds are directly stolen, but the protocol holds more ETH than the operator-configured ceiling, violating the invariant the limit is meant to enforce.

**Impact: Low — Contract fails to deliver promised returns (deposit cap), but does not lose value.**

### Likelihood Explanation
The condition is met whenever `totalAssetDeposits` is exactly at the limit, which is a natural state as the cap is approached during normal operation. Any unprivileged depositor calling `depositETH` at that moment triggers the overshoot with no special setup required.

### Recommendation
Include the incoming `amount` in the ETH branch, matching the ERC-20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

### Proof of Concept
1. Admin sets ETH deposit limit to 1 000 ETH via `lrtConfig`.
2. Through normal deposits, `getTotalAssetDeposits(ETH_TOKEN)` reaches exactly 1 000 ETH.
3. Attacker (or any user) calls `depositETH{value: 100 ether}(0, "")`.
4. Inside `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 100 ether)`:
   - `totalAssetDeposits = 1000e18`
   - ETH branch: `1000e18 > 1000e18` → `false` → no revert
5. `_mintRsETH` executes; total ETH deposits become 1 100 ETH — 10 % above the configured cap.
6. For comparison, a 100 ETH ERC-20 deposit at the same state would evaluate `1000e18 + 100e18 > 1000e18` → `true` → `MaximumDepositLimitReached` revert.

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
