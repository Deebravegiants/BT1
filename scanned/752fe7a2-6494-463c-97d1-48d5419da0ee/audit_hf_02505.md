# [M] Admin Key Trust on USDC Pool Owner

## Summary
Severity: Medium
Contest weight: 0.5950
Dataset id: 13387
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Whiteheart protocol, there is a privileged account that plays a critical role in governing and regulating the system-wide operations (e.g., parameter settings). Specifically, our analysis with the USDC pool shows that there is an owner account that can set up the lockup period as well as whitelist specific whAsset addresses to open positions using the USDC pool.
To elaborate, we show below the _exercise() routine that is responsible for exercising the put options. The exercise operation involves the unlocking of pool assets after option expiration (line 312) or the profit payment (line 315) before expiration.
```solidity
function _exercise(uint tokenId, address owner)
    internal
    returns (uint optionProfit, uint amount)
{
    Underlying storage _underlying = underlying[tokenId];
    amount = _underlying.amount;
    if (_underlying.expiration < block.timestamp) {
        pool.unlock(tokenId);
        optionProfit = 0;
    } else
        optionProfit = _payProfit(owner, tokenId, _underlying.strike, _underlying.amount);
}
```
However, both unlocking (via pool.unlock()) and profit payment (via pool.send()) are guarded with a modifier, i.e., onlyWHAssets. This modifier is regulated by the powerful owner account. In other words, the funds from option buys may be locked in the contract if the owner account somehow removes the whAsset addresses from being whitelisted to open a position.
```solidity
function unlock(uint256 id)
    external
    override
    onlyWHAssets
{
    LockedLiquidity storage ll = lockedLiquidity[msg.sender][id];
    require(ll.locked, "LockedLiquidity with such id has already unlocked");
    ll.locked = false;
    lockedPremium = lockedPremium.sub(ll.premium);
    lockedAmount = lockedAmount.sub(ll.amount);
    emit Profit(id, ll.premium);
}

function send(uint id, address payable to, uint256 amount, uint _payKeep3r)
    external
    override
    onlyWHAssets
{
    LockedLiquidity storage ll = lockedLiquidity[msg.sender][id];
    require(ll.locked, "LockedLiquidity with such id has already unlocked");
    require(to != address(0));
    ll.locked = false;
    lockedPremium = lockedPremium.sub(ll.premium);
    lockedAmount = lockedAmount.sub(ll.amount);
    uint transferAmount = amount > ll.amount ? ll.amount : amount;
    token.safeTransfer(to, transferAmount.sub(_payKeep3r));
    if (_payKeep3r > 0)
        owedToKeep3r = owedToKeep3r.add(_payKeep3r);
    if (transferAmount <= ll.premium)
        emit Profit(id, ll.premium - transferAmount);
    else
        emit Loss(id, transferAmount - ll.premium);
}
```

## Recommendation
While it is appropriate to have a whitelist capability to open a position, the close operation should not be blocked. In other words, the above two functions, i.e., unlock() and send(), do not need the onlyWHAssets modifier.
