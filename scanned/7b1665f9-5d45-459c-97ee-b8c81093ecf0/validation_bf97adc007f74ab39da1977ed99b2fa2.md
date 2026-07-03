### Title
ETH Deposit Limit Check Omits Deposit Amount, Allowing Limit Bypass - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit()` uses an inconsistent check for ETH versus ERC20 tokens. For ERC20 assets it correctly checks `totalAssetDeposits + amount > depositLimit`, but for ETH it only checks `totalAssetDeposits > depositLimit`, omitting the incoming `amount`. This mirrors the exact wrong-variable pattern in the reference report: a validation function checks a static value instead of the actual computed/incoming quantity, allowing the enforced constraint to be silently bypassed.

### Finding Description
In `LRTDepositPool.sol`, the internal function `_checkIfDepositAmountExceedesCurrentLimit` is responsible for enforcing the per-asset deposit cap set in `LRTConfig`:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)); // ← amount not included
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct for ERC20
}
```

For ETH, the check returns `true` (i.e., "limit exceeded") only when the *existing* total already surpasses the cap. The incoming `amount` is never added. As long as `totalAssetDeposits ≤ depositLimit`, the function returns `false` regardless of how large `amount` is, and the deposit proceeds.

This function is called from `_beforeDeposit`, which is invoked by the public `depositETH` entry point:

```solidity
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId)
    external payable nonReentrant whenNotPaused onlySupportedAsset(LRTConstants.ETH_TOKEN)
{
    uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);
    _mintRsETH(rsethAmountToMint);
    ...
}
```

### Impact Explanation
Any unprivileged depositor can call `depositETH` with an arbitrarily large `msg.value` when `totalAssetDeposits` is at or just below the configured limit. The deposit limit — a risk-management parameter set by the admin — is completely bypassed for ETH. This allows the protocol to mint rsETH beyond the intended cap, potentially leading to protocol insolvency if the limit was sized to ensure the protocol can back all outstanding rsETH. At minimum, the protocol fails to deliver its promised deposit-cap guarantee for ETH while correctly enforcing it for all ERC20 LSTs.

**Impact: Low (contract fails to deliver promised returns) to Critical (protocol insolvency), depending on the operational significance of the ETH deposit cap.**

### Likelihood Explanation
The entry path is fully public and requires no special role. Any depositor who observes `totalAssetDeposits` approaching the ETH limit can immediately exploit this by sending a large ETH deposit. The inconsistency between the ETH and ERC20 branches makes this easy to trigger deliberately.

### Recommendation
Add `amount` to the ETH branch, matching the ERC20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

### Proof of Concept
1. Admin sets `depositLimitByAsset(ETH_TOKEN) = 1000 ether`.
2. Current `getTotalAssetDeposits(ETH_TOKEN)` returns `999 ether`.
3. Attacker calls `depositETH{value: 500 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 500 ether)` evaluates `999e18 > 1000e18` → `false` → limit not exceeded.
5. `_mintRsETH` mints rsETH for 500 ETH, pushing total deposits to 1499 ETH — 49.9% above the intended cap.
6. For comparison, a 500-token ERC20 deposit at the same state would correctly revert: `999e18 + 500e18 > 1000e18` → `true`. [1](#0-0) [2](#0-1) [3](#0-2)

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
