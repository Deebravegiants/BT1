# [M] Zero fee to open position

## Summary
Severity: Medium
Reporter: Bauer
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L202
Type: audit-issue

## Details
# Zero fee to open position

## Summary
Zero fee to open position
## Vulnerability Detail
The `open_position()` function allows a user to open a new undercollateralized loan and assume a leveraged spot position in a specific token. Inside the function, if the token_in_amount  is smaller ,the fee will be 0.

```solidity
   # charge fee
    fee: uint256 = token_in_amount * self.trade_open_fee / PERCENTAGE_BASE
    assert self.margin[_account][_debt_token] >= fee, "not enough margin for fee"
    self.margin[_account][_debt_token] -= fee
    self._distribute_trading_fee(_debt_token, fee)

    log PositionOpened(_account, position)

    return position_uid, amount_bought
```

## Impact
Zero fee to open position

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L202
## Tool used

Manual Review

## Recommendation
if the fee is zero ,revert.
