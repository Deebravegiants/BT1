# [M] [Tomo-M3] Approve max has risk

## Summary
Severity: Medium
Reporter: Tomo
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/lib/UniversalERC20.sol#L36-L48
Type: audit-issue

## Details
# [Tomo-M3] Approve max has risk

## Summary
Approve max has risk

## Vulnerability Detail

The `universalApproveMax()` is using unlimited approval. It is true that using this function only whitelisted contracts but if these contracts are hacked, the funds of this project would also be threatened due to unlimited approval.

Although unlimited approval is used by various DeFi platforms to minimize transaction fees and improve user experience, it introduces security risks as well.

You can see the detail of this issue.

[https://kalis.me/unlimited-erc20-allowances/](https://kalis.me/unlimited-erc20-allowances/)

[https://medium.com/@rodrigoherrerai/understanding-the-problem-of-erc20-unlimited-approval-from-first-principles-d2eaf6b4ea0e](https://medium.com/@rodrigoherrerai/understanding-the-problem-of-erc20-unlimited-approval-from-first-principles-d2eaf6b4ea0e)

## Impact

In the term of smart contract security, the approve max doesn’t recommend it.

## Code Snippet

[https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/lib/UniversalERC20.sol#L36-L48](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/lib/UniversalERC20.sol#L36-L48)

```solidity
function universalApproveMax(
    IERC20 token,
    address to,
    uint256 amount
) internal {
    uint256 allowance = token.allowance(address(this), to);
    if (allowance < amount) {
        if (allowance > 0) {
            token.safeApprove(to, 0);
        }
        token.safeApprove(to, type(uint256).max);
    }
}
```

## Tool used

Manual Review

## Recommendation

Consider changing `universalApproveMax()` to only the required amount, or rather using increaseERC20Allowance() and decreaseERC20Allowance().
