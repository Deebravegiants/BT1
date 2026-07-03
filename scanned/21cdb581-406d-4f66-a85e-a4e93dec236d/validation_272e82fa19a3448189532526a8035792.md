### Title
ETH Deposit Limit Not Enforced — New Deposit Amount Excluded from Cap Check - (File: contracts/LRTDepositPool.sol)

### Summary

`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` applies an asymmetric check for ETH versus ERC-20 assets. For ERC-20 tokens the incoming `amount` is added to `totalAssetDeposits` before comparing against the cap, but for ETH the incoming deposit amount is silently dropped from the comparison. Any depositor can therefore call `depositETH` with an arbitrarily large value and bypass the `depositLimitByAsset` cap entirely, as long as the pre-existing total has not already crossed the limit.

### Finding Description

```solidity
// contracts/LRTDepositPool.sol  lines 676-682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount ignored
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct for ERC-20
}
``` [1](#0-0) 

For ETH the function only asks "has the limit already been exceeded?" — it never asks "would this deposit exceed the limit?" The parameter `amount` (which equals `msg.value`) is received but never used in the ETH branch. The ERC-20 branch correctly adds `amount` to `totalAssetDeposits`.

The caller path is fully public and unprivileged:

```
depositETH(minRSETHAmountExpected, referralId)   [payable, nonReentrant, whenNotPaused]
  └─ _beforeDeposit(ETH_TOKEN, msg.value, ...)
       └─ _checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, msg.value)
            └─ returns (totalAssetDeposits > depositLimit)   // msg.value never used
``` [2](#0-1) [3](#0-2) 

### Impact Explanation

`depositLimitByAsset` is the protocol's primary risk-management cap controlling how much ETH can be restaked through EigenLayer. Bypassing it allows an unbounded amount of ETH to be deposited and rsETH minted beyond the intended ceiling. Excess ETH that cannot be delegated to EigenLayer strategies (e.g., because the strategy's own cap is reached) accumulates idle in the deposit pool, making it temporarily inaccessible for yield generation and potentially undeployable until governance intervenes. This matches the **Low** impact tier: the contract fails to deliver the promised deposit-cap guarantee, though deposited ETH is not directly stolen.

### Likelihood Explanation

The entry point `depositETH` is public and requires no special role. Any depositor who observes that `totalAssetDeposits < depositLimitByAsset(ETH)` can send an arbitrarily large ETH deposit in a single transaction and the check will pass. No front-running, brute-force, or privileged access is required.

### Recommendation

Include the incoming deposit amount in the ETH branch, mirroring the ERC-20 logic:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [4](#0-3) 

Also update `getAssetCurrentLimit` which has the same off-by-one issue (`>` instead of `>=`) and would report a non-zero remaining limit even when the cap is exactly met. [5](#0-4) 

### Proof of Concept

Assume `depositLimitByAsset(ETH) = 100_000 ether` and `totalAssetDeposits(ETH) = 99_999 ether`.

1. Attacker calls `depositETH{value: 500_000 ether}(0, "")`.
2. `_checkIfDepositAmountExceedesCurrentLimit(ETH, 500_000 ether)` evaluates `99_999 ether > 100_000 ether` → `false` → no revert.
3. `getRsETHAmountToMint` mints rsETH for the full 500,000 ETH.
4. `totalAssetDeposits(ETH)` is now 599,999 ETH — nearly 6× the intended cap — with no protocol-level rejection.

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
