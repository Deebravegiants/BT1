# [M] originationFee may result in the borrower ac-

## Summary
Severity: Medium
Contest weight: 0.4165
Dataset id: 17611
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
contest. This scope was only reviewed by WatchPug and relates to these three PRs:
1. Lending deposit cap
2. Fee accrual modification
3. CRV staking
originationFee may result in the borrower account becoming liquidatable immediately.
When checking riskEngine.isBorrowAllowed(), the originationFee of the borrow is not considered. Thus, when originationFee is large enough, the borrower account becomes liquidatable immediately.
For example:
Let's say USDC's originationFee is 30%;
Alice has 100USDC, and 0 debt in her account; Alice borrowed 400USDC, received only 280USDC after the originationFee; Alice's account is now liquidatable. Actually, in the case above, Alice's account won't even get liquidated as all the assets are worth (380 USDC) less than the total debt (400USDC).
originationFee may result in the borrower account becoming liquidatable immediately.

## Recommendation
Consider asserting riskEngine.isAccountHealthy() after the borrow:
```solidity
function borrow(address account, address token, uint amt)
    external
    whenNotPaused
    onlyOwner(account)
{
    if (registry.LTokenFor(token) == address(0))
        revert Errors.LTokenUnavailable();
    if (IAccount(account).hasAsset(token) == false)
        IAccount(account).addAsset(token);
    if (ILToken(registry.LTokenFor(token)).lendTo(account, amt))
        IAccount(account).addBorrow(token);
    if (!riskEngine.isAccountHealthy(account))
        revert Errors.RiskThresholdBreached();
    emit Borrow(account, msg.sender, token, amt);
}
```
riskEngine.isBorrowAllowed should be removed as it's no longer needed.
Pushed a commit to remove the redundant call to riskEngine, you can find it here.
