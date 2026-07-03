### Title
Unbounded `setMinRsEthAmountToWithdraw()` Can Permanently Block All Withdrawal Requests - (File: contracts/LRTWithdrawalManager.sol)

### Summary
`LRTWithdrawalManager.setMinRsEthAmountToWithdraw()` has no upper-bound validation. Setting it to an arbitrarily large value (e.g., `type(uint256).max`) causes every call to `initiateWithdrawal()` and `instantWithdrawal()` to revert, temporarily freezing all rsETH holders out of the withdrawal path for the affected asset.

### Finding Description
`setMinRsEthAmountToWithdraw()` is an admin-only setter with no ceiling on the value it accepts:

```solidity
// LRTWithdrawalManager.sol L330-333
function setMinRsEthAmountToWithdraw(address asset, uint256 minRsEthAmountToWithdraw_)
    external onlyLRTAdmin
{
    minRsEthAmountToWithdraw[asset] = minRsEthAmountToWithdraw_;
    emit MinAmountToWithdrawUpdated(asset, minRsEthAmountToWithdraw_);
}
``` [1](#0-0) 

The stored value is enforced as a hard gate in both user-facing withdrawal entry points:

```solidity
// initiateWithdrawal – L162
if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
    revert InvalidAmountToWithdraw();
}
``` [2](#0-1) 

```solidity
// instantWithdrawal – L224
if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
    revert InvalidAmountToWithdraw();
}
``` [3](#0-2) 

Contrast this with `setWithdrawalDelayBlocks()`, which correctly enforces a ceiling:

```solidity
// L339-340
if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();
``` [4](#0-3) 

No equivalent ceiling exists for `minRsEthAmountToWithdraw`.

### Impact Explanation
If `minRsEthAmountToWithdraw[asset]` is set to `type(uint256).max` (or any value exceeding the total rsETH supply), every call to `initiateWithdrawal()` and `instantWithdrawal()` for that asset reverts unconditionally. rsETH holders who wish to exit their position via that asset are completely blocked — their rsETH is locked in their wallets with no withdrawal path available until the admin resets the value. This constitutes **temporary freezing of funds** (Medium severity per the allowed impact scope).

### Likelihood Explanation
The `onlyLRTAdmin` role is a single privileged address. The setter requires no timelock, no multisig confirmation at the contract level, and no on-chain delay before taking effect. A single erroneous or malicious call immediately blocks all withdrawals for the affected asset. The absence of any guardrail makes an accidental misconfiguration (e.g., passing a value in the wrong unit) equally dangerous.

### Recommendation
Add an explicit upper-bound check mirroring the pattern already used in `setWithdrawalDelayBlocks()`:

```solidity
uint256 public constant MAX_MIN_RSETH_TO_WITHDRAW = 1000 ether; // example ceiling

function setMinRsEthAmountToWithdraw(address asset, uint256 minRsEthAmountToWithdraw_)
    external onlyLRTAdmin
{
    if (minRsEthAmountToWithdraw_ > MAX_MIN_RSETH_TO_WITHDRAW)
        revert ExceedMaxMinWithdrawAmount();
    minRsEthAmountToWithdraw[asset] = minRsEthAmountToWithdraw_;
    emit MinAmountToWithdrawUpdated(asset, minRsEthAmountToWithdraw_);
}
```

Additionally, consider routing the setter through a timelock or multisig so that users have advance notice of any change and can act before it takes effect.

### Proof of Concept
1. Admin calls `setMinRsEthAmountToWithdraw(ETH_TOKEN, type(uint256).max)`.
2. User holds 10 rsETH and calls `initiateWithdrawal(ETH_TOKEN, 10e18, "")`.
3. Check at L162: `10e18 < type(uint256).max` → `true` → `revert InvalidAmountToWithdraw()`.
4. User also tries `instantWithdrawal(ETH_TOKEN, 10e18, "")`.
5. Check at L224: same revert.
6. All rsETH holders are blocked from exiting via ETH until the admin resets the value. No on-chain mechanism forces or time-bounds that reset. [5](#0-4)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L150-178)
```text
    function initiateWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        override
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L224-226)
```text
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L330-333)
```text
    function setMinRsEthAmountToWithdraw(address asset, uint256 minRsEthAmountToWithdraw_) external onlyLRTAdmin {
        minRsEthAmountToWithdraw[asset] = minRsEthAmountToWithdraw_;
        emit MinAmountToWithdrawUpdated(asset, minRsEthAmountToWithdraw_);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L338-344)
```text
    function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
        // Set an upper limit of no more than 16 days
        if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();

        withdrawalDelayBlocks = withdrawalDelayBlocks_;
        emit WithdrawalDelayBlocksUpdated(withdrawalDelayBlocks);
    }
```
