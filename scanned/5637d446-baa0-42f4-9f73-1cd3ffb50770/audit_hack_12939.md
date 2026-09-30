# [M] When vault is paused, positions may be subject to unfair liquidation

## Summary
Severity: Medium
Reporter: 0x00ffDa
Source: https://github.com/Unstoppable-DeFi/unstoppable-dex-audit/blob/4153c3e67ccc080032ba0bbaffd9a0c56a573070/contracts/margin-dex/Vault.vy#L673
Type: audit-issue

## Details
# When vault is paused, positions may be subject to unfair liquidation

## Summary
When the Vault contract is in a paused state, it does not allow traders to add to their margin accounts. However, liquidation is allowed in that state, which can put traders at risk of liquidation with no recourse.

## Vulnerability Detail
The Unstoppable Vault contract can be put in an administrative pause state during which new orders are not accepted. This is done by the admin address calling `set_is_accepting_new_orders()` to set the `is_accepting_new_orders` state flag to True. This also happens automatically when the Vault encounters bad debt.

When the Vault is in this paused state, a user with debt can only supplement a position with existing (but unallocated) margin in their account (via the `add_margin()` function, or possibly `swap_margin()`). But they cannot add outside funds to their margin account while the vault is paused even though liquidation is permitted in this state. So, if they either have no spare margin in the Vault when funding is paused, or they do not have enough margin to keep their positions from becoming over-leveraged, they are at risk of unfair liquidation.

For reference: [a similar audit finding](https://github.com/sherlock-audit/2023-02-blueberry-judging/issues/290)

## Impact
User funds in margin trades are at risk of loss during periods of vault administration such as resolving bad debt.

## Code Snippet
https://github.com/Unstoppable-DeFi/unstoppable-dex-audit/blob/4153c3e67ccc080032ba0bbaffd9a0c56a573070/contracts/margin-dex/Vault.vy#L673
```javascript
nonreentrant("lock")
@external
def fund_account(_token: address, _amount: uint256):
    """
    @notice
        Allows a user to fund his _token margin.
    """
    assert self.is_accepting_new_orders, "funding paused"
    assert self.is_whitelisted_token[_token], "token not whitelisted"
    self.margin[msg.sender][_token] += _amount
    self._safe_transfer_from(_token, msg.sender, self, _amount)
    log AccountFunded(msg.sender, _amount, _token)

```

## Tool used

Manual Review

## Recommendation
Allow `fund_account_eth()` and `fund_account()` even when the vault is not accepting orders.
