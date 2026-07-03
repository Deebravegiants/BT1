### Title
ETH Deposit Limit Check Omits Deposit Amount, Allowing Limit Bypass - (File: contracts/LRTDepositPool.sol)

### Summary

The `_checkIfDepositAmountExceedesCurrentLimit` function in `LRTDepositPool.sol` contains a conditional branch for ETH that omits the incoming deposit `amount` from the limit comparison. The ERC20 branch correctly includes `amount`, but the ETH branch does not. This structural asymmetry — directly analogous to the misplaced-bracket conditional logic described in the external report — allows any ETH depositor to push total ETH deposits past the configured deposit limit.

### Finding Description

`_checkIfDepositAmountExceedesCurrentLimit` is called by `_beforeDeposit` for every deposit, and its return value gates whether `MaximumDepositLimitReached` is thrown:

```solidity
// contracts/LRTDepositPool.sol lines 676-682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount missing
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct
}
``` [1](#0-0) 

For ETH the function returns `true` (i.e., "limit exceeded") only when `totalAssetDeposits` **already** exceeds the cap — it never tests whether adding the new deposit would cross the cap. For ERC20 assets the test is `totalAssetDeposits + amount > limit`, which is correct.

Consequence: if `totalAssetDeposits == limit - 1 wei`, the ETH check returns `false` and any deposit amount is accepted, pushing the total arbitrarily above the limit. The ERC20 path would correctly reject the same scenario.

The caller `_beforeDeposit` (lines 648–670) relies entirely on this function to enforce the cap before minting rsETH:

```solidity
if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
    revert MaximumDepositLimitReached();
}
``` [2](#0-1) 

And `depositETH` (lines 76–93) is the publicly reachable entry point:

```solidity
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId)
    external payable nonReentrant whenNotPaused onlySupportedAsset(LRTConstants.ETH_TOKEN)
{
    uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);
    _mintRsETH(rsethAmountToMint);
    ...
}
``` [3](#0-2) 

### Impact Explanation

The deposit limit is a protocol-level safety cap. Bypassing it allows more ETH than intended to flow into EigenLayer strategies via `NodeDelegator`. If the cap was sized to match EigenLayer strategy capacity, operator delegation limits, or slashing exposure budgets, exceeding it can cause the protocol to accept liabilities it cannot service — a path to protocol insolvency. At minimum, the protocol fails to enforce its own stated deposit ceiling, constituting a failure to deliver promised protocol invariants.

**Impact: Low — Contract fails to deliver promised returns (deposit limit invariant broken); escalates toward Critical (protocol insolvency) if the limit is a hard EigenLayer capacity guard.**

### Likelihood Explanation

Any unprivileged ETH depositor can trigger this. No special role, front-running, or oracle manipulation is required. The only precondition is that `totalAssetDeposits` for ETH is below (but near) the configured limit, which is the normal operating state of a live protocol. Likelihood is **Medium**.

### Recommendation

Add the `amount` parameter to the ETH branch, mirroring the ERC20 branch:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // fixed
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

### Proof of Concept

1. Admin sets `depositLimitByAsset(ETH_TOKEN) = 1000 ether`.
2. Protocol accumulates `999.9 ether` in ETH deposits (`totalAssetDeposits = 999.9 ether`).
3. Attacker calls `depositETH{value: 500 ether}(...)`.
4. `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 500 ether)` evaluates `999.9 ether > 1000 ether` → `false` → no revert.
5. `_mintRsETH` mints rsETH for 500 ETH; total ETH deposits become `1499.9 ether`, 50% above the cap.
6. The same call with an ERC20 asset would evaluate `999.9 + 500 > 1000` → `true` → `MaximumDepositLimitReached` revert. [1](#0-0) [4](#0-3)

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
