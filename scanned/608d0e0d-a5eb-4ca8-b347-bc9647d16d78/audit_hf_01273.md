# [M] Re-entrancy risk with ERC777 tokens in multiple functions

## Summary
Severity: Medium
Contest weight: 0.5950
Dataset id: 6023
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The deposit and depositWithPermit functions in the contract allow users to deposit ERC20 tokens into the contract. However, these functions do not consider the potential re-entrancy risks associated with ERC777 tokens.  
ERC777 tokens have additional hooks or callbacks that can be triggered during token transfers. These hooks, if not properly handled, can lead to re-entrancy vulnerabilities, where an attacker can potentially re-enter the contract and execute malicious code before the original execution is complete.  
If an attacker deposits an ERC777 token and exploits the re-entrancy vulnerability in either the deposit or depositWithPermit function, they may be able to circumvent certain security checks or manipulate the contract state in unintended ways. For example, an attacker could potentially bypass the share lock period by using the token's transfer hooks to transfer the newly minted shares to another address before the lock period is enforced.  
```solidity
/**
* @notice Allows users to deposit into the BoringVault, if this contract is not paused.
*/
function deposit(ERC20 depositAsset, uint256 depositAmount, uint256 minimumMint)
public
payable
requiresAuth
returns (uint256 shares)
{
    if (isPaused) revert TellerWithMultiAssetSupport__Paused();
    if (!isSupported[depositAsset]) revert TellerWithMultiAssetSupport__AssetNotSupported();
    if (address(depositAsset) == NATIVE) {
        if (msg.value == 0) revert TellerWithMultiAssetSupport__ZeroAssets();
        nativeWrapper.deposit{value: msg.value}();
        depositAmount = msg.value;
        shares = depositAmount.mulDivDown(ONE_SHARE, accountant.getRateInQuoteSafe(nativeWrapper));
        if (shares < minimumMint) revert TellerWithMultiAssetSupport__MinimumMintNotMet();
        // `from` is address(this) since user already sent value.
        nativeWrapper.safeApprove(address(vault), depositAmount);
        vault.enter(address(this), nativeWrapper, depositAmount, msg.sender, shares);
    } else {
        if (msg.value > 0) revert TellerWithMultiAssetSupport__DualDeposit();
        shares = _erc20Deposit(depositAsset, depositAmount, minimumMint, msg.sender);
    }
    _afterPublicDeposit(msg.sender, depositAsset, depositAmount, shares, shareLockPeriod);
}
```
```solidity
/**
* @notice Allows users to deposit into BoringVault using permit.
*/
function depositWithPermit(
    ERC20 depositAsset,
    uint256 depositAmount,
    uint256 minimumMint,
    uint256 deadline,
    uint8 v,
    bytes32 r,
    bytes32 s
) external requiresAuth returns (uint256 shares) {
    if (isPaused) revert TellerWithMultiAssetSupport__Paused();
    if (!isSupported[depositAsset]) revert TellerWithMultiAssetSupport__AssetNotSupported();
    try depositAsset.permit(msg.sender, address(vault), depositAmount, deadline, v, r, s) {}
    catch {
        if (depositAsset.allowance(msg.sender, address(vault)) < depositAmount) {
            revert TellerWithMultiAssetSupport__PermitFailedAndAllowanceTooLow();
        }
    }
    shares = _erc20Deposit(depositAsset, depositAmount, minimumMint, msg.sender);
    _afterPublicDeposit(msg.sender, depositAsset, depositAmount, shares, shareLockPeriod);
}
```
An example Token list can be seen from below :  
• PNT  
• IMBTC  
• Superfluid Token  
• XDAI Token

## Recommendation
To mitigate the potential re-entrancy risk with ERC777 tokens, it is recommended to implement a re-entrancy guard or a mutability check before any state-changing operations in both the deposit and depositWithPermit functions.
