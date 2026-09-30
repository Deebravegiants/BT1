# [M] Admin can drain market of double-entrypoint ERC-20 using `AdminImpl::ownerWithdrawUnsupportedTokens`

## Summary
Severity: Medium
Contest weight: 0.4614
Dataset id: 19118
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`AdminImpl::ownerWithdrawUnsupportedTokens` is intended to allow the owner to withdraw any unsupported ERC-20 token which might have ended up at the Dolomite Margin address. If a double-entrypoint ERC-20 token is listed as a market on Dolomite, it is possible for the admin to drain the entire token balance.

Such tokens are problematic because the legacy token delegates its logic to the new token, meaning that two separate addresses are used to interact with the same token. Previous examples include TUSD which resulted in [vulnerability when integrated into Compound](https://blog.openzeppelin.com/compound-tusd-integration-issue-retrospective/). This highlights the importance of carefully selecting the collateral token, especially as this type of vulnerability is not easily detectable. In addition, it is not unrealistic to expect that an upgradeable collateral token could become a double-entrypoint token in the future, e.g. USDT, so this must also be considered.

By passing the legacy token address of a double-entrypoint token as argument to [`AdminImpl::ownerWithdrawUnsupportedTokens`](https://github.com/feat/dolomite-margin/blob/e10f14320ece20d7492e8e68400333c5c7dec656/contracts/protocol/impl/AdminImpl.sol#L183), the admin can drain the entire token balance. The legacy token will not have a valid market id as it has not been added to Dolomite, so [`AdminImpl::_requireNoMarket`](https://github.com/feat/dolomite-margin/blob/e10f14320ece20d7492e8e68400333c5c7dec656/contracts/protocol/impl/AdminImpl.sol#L589) will pass.
```solidity
function ownerWithdrawUnsupportedTokens(
    Storage.State storage state,
    address token,
    address recipient
)
    public
    returns (uint256)
{
    _requireNoMarket(state, token);

    uint256 balance = IERC20Detailed(token).balanceOf(address(this));
    token.transfer(recipient, balance);

    emit LogWithdrawUnsupportedTokens(token, balance);

    return balance;
}
```
However, function calls on the legacy token will be forwarded to the new version, so the balance returned will be that of the token in the protocol, which will be transferrable to the admin.

This finding would have a critical impact, leaving the protocol in an insolvent state at the expense of its users; however, the likelihood is low due to external assumptions, and so we evaluate the severity as MEDIUM.

## Recommendation
Loop through all supported Dolomite Margin markets and validate the collateral token balances before withdrawing unsupported tokens are equal to the token balances after.
