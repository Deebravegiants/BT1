# [M] Lack of `safeApprove

## Summary
Severity: Medium
Contest weight: 0.4176
Dataset id: 3632
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[TopUpAction.sol#L50](https://github.com/code-423n4/2022-04-backd/blob/c856714a50437cb33240a5964b63687c9876275b/backd/contracts/actions/topup/TopUpAction.sol#L50)  
[LiquidityPool.sol#L721](https://github.com/code-423n4/2022-04-backd/blob/c856714a50437cb33240a5964b63687c9876275b/backd/contracts/pool/LiquidityPool.sol#L721)  

OpenZeppelin’s `safeApprove()` will revert if the account already is approved and the new `safeApprove()` is done with a non-zero value
    
        function safeApprove(
            IERC20 token,
            address spender,
            uint256 value
        ) internal {
            // safeApprove should only be called when setting an initial allowance,
            // or when resetting it to zero. To increase and decrease it, use
            // 'safeIncreaseAllowance' and 'safeDecreaseAllowance'
            require(
                (value == 0) || (token.allowance(address(this), spender) == 0),
                "SafeERC20: approve from non-zero to non-zero allowance"
            );
            _callOptionalReturn(token, abi.encodeWithSelector(token.approve.selector, spender, value));
        }

[OpenZeppelin/SafeERC20.sol#L45-L58](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/fcf35e5722847f5eadaaee052968a8a54d03622a/contracts/token/ERC20/utils/SafeERC20.sol#L45-L58)

## Proof of Concept
There are multiple places where `safeApprove()` is called a second time without setting the value to zero first.

`register()` calls `lockFunds()` for each user registration, and since users will use the same tokens and staker vaults, the second user’s `register()` call will fail:
    
    File: backd/contracts/actions/topup/TopUpAction.sol   #1
    
    36       function lockFunds(
    37           address stakerVaultAddress,
    38           address payer,
    39           address token,
    40           uint256 lockAmount,
    41           uint256 depositAmount
    42       ) external {
    43           uint256 amountLeft = lockAmount;
    44           IStakerVault stakerVault = IStakerVault(stakerVaultAddress);
    45   
    46           // stake deposit amount
    47           if (depositAmount > 0) {
    48               depositAmount = depositAmount > amountLeft ? amountLeft : depositAmount;
    49               IERC20(token).safeTransferFrom(payer, address(this), depositAmount);
    50               IERC20(token).safeApprove(stakerVaultAddress, depositAmount);

[TopUpAction.sol#L36-L50](https://github.com/code-423n4/2022-04-backd/blob/c856714a50437cb33240a5964b63687c9876275b/backd/contracts/actions/topup/TopUpAction.sol#L36-L50)  

The changing of either the staker or an lp token is behind a time-lock, and once the time has passed, the changed variables rely on this function:
    
    File: backd/contracts/pool/LiquidityPool.sol   #2
    
    717       function _approveStakerVaultSpendingLpTokens() internal {
    718           address staker_ = address(staker);
    719           address lpToken_ = address(lpToken);
    720           if (staker_ == address(0) || lpToken_ == address(0)) return;
    721           IERC20(lpToken_).safeApprove(staker_, type(uint256).max);
    722       }

[LiquidityPool.sol#L717-L722](https://github.com/code-423n4/2022-04-backd/blob/c856714a50437cb33240a5964b63687c9876275b/backd/contracts/pool/LiquidityPool.sol#L717-L722)  

If a bug is found in a new `staker` or `lpToken` and the governor wishes to change back to the old one(s), the governor will have to wait for the time-lock delay only to find out that the old value(s) cause the code to revert.

I’ve filed the other more-severe instances as a separate high-severity issue, and flagged the remaining low-severity instances in my QA report.

## Recommendation
Always do `safeApprove(0)` if the allowance is being changed, or use `safeIncreaseAllowance()`.

It should be noted that the second example referring to `_approveStakerVaultSpendingLpTokens()` is not an issue. This is neither a member variable that can be updated nor is it behind a time lock. Both the `staker` and `lpToken` can only be set once and hence the `safeApprove` in the aforementioned function can only be called once.

**[chase-manning (Backd) resolved](https://github.com/code-423n4/2022-04-backd-findings/issues/180)** resolved
