### Title
ETH Deposit Limit Check Omits New Deposit Amount, Allowing Limit Bypass - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit()` applies an asymmetric and incomplete check for ETH deposits: it tests only whether the current total already exceeds the limit, without including the incoming deposit amount. The ERC20 path correctly adds `amount` to the current total before comparing. Any depositor can push ETH holdings above the configured deposit limit.

### Finding Description
In `_checkIfDepositAmountExceedesCurrentLimit` (lines 676–682 of `LRTDepositPool.sol`), the ETH branch omits the new deposit amount from the comparison:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)); // ← `amount` not included
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct for ERC20
}
```

The ETH check returns `true` (limit exceeded) only when `totalAssetDeposits` already surpasses the cap before the deposit lands. As long as the running total is at or below the cap, the function returns `false` regardless of how large `msg.value` is, and `_beforeDeposit` proceeds without reverting.

The ERC20 path correctly evaluates `totalAssetDeposits + amount > depositLimit`, which is the intended semantics for both asset types. [1](#0-0) 

The function is called from `_beforeDeposit`, which is invoked by the public `depositETH` entry point: [2](#0-1) [3](#0-2) 

### Impact Explanation
The deposit limit for ETH is a protocol-level risk control (analogous to a position cap). When it is bypassed, the protocol accumulates more ETH exposure in EigenLayer strategies than governance has approved. This constitutes the contract failing to deliver its promised constraint without directly losing user value.

**Impact: Low** — Contract fails to deliver promised returns (deposit cap enforcement), but deposited funds are not lost.

### Likelihood Explanation
The `depositETH` function is the primary public entry point for any ETH depositor. No special role or precondition is required beyond the contract being unpaused and the ETH asset being supported. The condition that makes the bypass possible (current total ≤ limit) is the normal operating state of the protocol.

**Likelihood: Medium** — Reachable by any unprivileged depositor during normal protocol operation.

### Recommendation
Add `amount` to the ETH branch to match the ERC20 path:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

### Proof of Concept
1. Admin sets ETH deposit limit to 100,000 ETH via `LRTConfig.updateAssetDepositLimit`.
2. Current `getTotalAssetDeposits(ETH_TOKEN)` = 99,999 ETH.
3. Attacker calls `depositETH{value: 2,000 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit` evaluates `99,999 > 100,000` → `false`; no revert.
5. 2,000 ETH is accepted; total becomes 101,999 ETH — 1,999 ETH above the configured cap.
6. The deposit limit is silently bypassed by any depositor in a single transaction.

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
