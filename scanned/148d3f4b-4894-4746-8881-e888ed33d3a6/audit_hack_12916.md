# [M] The Owner can use fees to reap traders.

## Summary
Severity: Medium
Reporter: shealtielanz
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L448C1-L457C25
Type: audit-issue

## Details
# The Owner can use fees to reap traders.

## Summary
The owner can set the `fees` to any amount, and traders will not know, so whenever they trade the fees charged from them will be so much and the owner could Immediately claim such `fees`.
**A word to the judge** "You might want to classify this as a low, but it's not tho it might arise via centralization the fee should be set within a particular threshold as the developers intended but forgot to implement correctly"
Although this might be a centralization issue, the impact is `high` and the protocol stated it
## Vulnerability Detail
The trade_open_fee variable ----> 
```vyper
# the fee charged to traders when opening a position
trade_open_fee: public(uint256) # 10 = 0.1%
```
An instance of this is in Vault.vy, here you can see that the open trade fee can be set to any amount desired by the owner.
```vyper
@external
def set_trade_open_fee(_fee: uint256):
    assert msg.sender == self.admin, "unauthorized"
    self.trade_open_fee = _fee
```
The `fee` should be set within a particular threshold that would protect `traders` in the case of any centralization issue, also where in my former report stated that the owner could be claimed by anyone, a malicious actor can simply claim ownership and increase the fees to a very high amount, where before traders realize due to there is no event to track the fee's update, the attacker would have claimed the `fees` accumulated by then.
## Impact
Here the traders can be reaped by anyone who is the owner, however, the set fee function in `Dca.vy` was implemented properly [Link here](https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L448C1-L457C25)to show that the developers didn't want this kind of issue to occur ----->
```vyper
event FeeUpdated:
    new_fee: uint256

@external
def set_fee(_fee: uint256):
    assert msg.sender == self.owner, "unauthorized"
    assert _fee < FEE_BASE, "invalid fee"
    assert _fee != self.fee, "new fee cannot be same as old fee"
    self.fee = _fee
    log FeeUpdated(_fee)
```
## Code Snippet
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1523C1-L1526C31
## Tool used

`Manual Review`

## Recommendation
Implement the `set_trade_open_fee()` function in a similar pattern you implemented the `set_fee()` function in Dca.vy
