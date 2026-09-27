# [M] In limitorders.vy and Dca.y users can create multiple orders with one approve

## Summary
Severity: Medium
Reporter: mahdiRostami
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L97-L98
Type: audit-issue

## Details
# In limitorders.vy and Dca.y users can create multiple orders with one approve

## Summary
in
```solidity
    allowance: uint256 = ERC20(_token_in).allowance(msg.sender, self)
    assert allowance >= _amount_in, "insufficient allowance"
```
User can create multiple limit orders in one token with one allowance, which make cause problems for takers when they want to execute orders.
## Vulnerability Details
**POC**
```python
def test_(spot_limit, usdc, weth, owner):
    amount_in = 100 * 10**6
    min_amount_out = 1 * 10**18
    valid_until = 99999999999

    usdc.approve(spot_limit, amount_in)

    spot_limit.post_limit_order(usdc, weth, amount_in, min_amount_out, valid_until)

    after = spot_limit.get_all_open_positions(owner)
    assert len(after) == 1
    spot_limit.post_limit_order(usdc, weth, amount_in, min_amount_out, valid_until)
    after2 = spot_limit.get_all_open_positions(owner)
    assert len(after2) == 2
```
## Impact
there are orders which cannot be executed.
## Code Snippet
instances:
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L97-L98
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L115-L117
## Tool used

Manual Review

## Recommendation
check for users orders and in checking allowance consider those orders as well
