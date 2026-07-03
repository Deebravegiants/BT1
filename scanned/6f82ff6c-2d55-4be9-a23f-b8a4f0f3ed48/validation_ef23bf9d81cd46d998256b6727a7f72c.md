### Title
ETH Deposit Limit Check Omits Current Deposit Amount, Allowing the Cap to Be Exceeded - (File: contracts/LRTDepositPool.sol)

### Summary
`_checkIfDepositAmountExceedesCurrentLimit` applies an asymmetric check for ETH versus LST assets. For LSTs the incoming `amount` is included in the comparison, but for ETH it is not. Any depositor can therefore exceed the ETH deposit cap by an arbitrary amount in a single transaction, rendering the limit a false protection.

### Finding Description
`_checkIfDepositAmountExceedesCurrentLimit` in `LRTDepositPool.sol` reads:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount not added
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct for LSTs
}
``` [1](#0-0) 

For ETH the function returns `true` (i.e. "limit exceeded") only when `totalAssetDeposits` **already** exceeds the cap — it never tests whether the incoming deposit would push the total over the cap. For every LST the incoming `amount` is correctly added before the comparison.

`depositETH` calls `_beforeDeposit`, which calls this check, so the flaw is on the critical deposit path. [2](#0-1) [3](#0-2) 

### Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

The `depositLimitByAsset` for ETH is the protocol's risk-management cap on total ETH exposure. Because the check never includes the current deposit amount, a single depositor can push `totalAssetDeposits` arbitrarily above the cap in one transaction (e.g., cap = 1 000 ETH, current total = 999 ETH, attacker deposits 10 000 ETH → total becomes 10 999 ETH). The cap is therefore a false invariant: it gives operators and users a false sense of security that ETH exposure is bounded, while in practice it is not. No funds are directly stolen, but the protocol silently accepts far more ETH than its risk parameters allow.

### Likelihood Explanation
**Medium.** The attack requires no special role, no flash loan, and no coordination. Any depositor who monitors the on-chain state and sees `totalAssetDeposits ≤ depositLimitByAsset` can send a single `depositETH` call with an arbitrarily large `msg.value`. The condition is trivially observable and the exploit is a single transaction.

### Recommendation
Add the incoming `amount` to the ETH branch, matching the LST branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [1](#0-0) 

### Proof of Concept
1. Admin sets ETH deposit limit to 1 000 ETH via `LRTConfig.updateAssetDepositLimit`.
2. Legitimate users deposit until `getTotalAssetDeposits(ETH_TOKEN) == 999 ETH`.
3. Attacker calls `depositETH{value: 10_000 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit` evaluates `999e18 > 1000e18` → `false` → deposit is not blocked.
5. `_mintRsETH` mints rsETH for 10 000 ETH; `totalAssetDeposits` is now 10 999 ETH — 10× the intended cap.
6. All subsequent ETH deposits are blocked (`10999 > 1000` → `true`), but the damage is done: the protocol holds 10× its intended ETH exposure. [1](#0-0) [3](#0-2)

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
