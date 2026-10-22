# [H] any whitelisted dex can directly call the `close_position`, `remove_margin` from vault.vy

## Summary
Severity: High
Reporter: 0xpinky
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L227
Type: audit-issue

## Details
# any whitelisted dex can directly call the `close_position`, `remove_margin` from vault.vy

## Summary

User can trade through the `MarginDex.vy` when they have valid position opened.

when there are access control in `MarginDex.vy` for closing the trade or removing the margin such that only the trading account can call these function with valid dex permission.

But when we look at the [close_position ](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L227) [remove_margin ](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L528) from the vault.vy , they don't have any restriction such that only the position owner can call , instead it allows to call by any valid dex. 

if any of the dex turns into malicious, it could disrupt trading by simply calling the `close_position` and `remove_marign` so that valid trader can not trade.

## Vulnerability Detail

lets look at the function `remove_margin` from `MarginDex.vy`
```vyper
def remove_margin(_trade_uid: bytes32, _amount: uint256):
    """
    @notice
        Allows traders to remove excess margin from a Trades underlying
        Vault position and increase leverage.
    """
    trade: Trade = self.open_trades[_trade_uid]
    assert (trade.account == msg.sender) or self.is_delegate[trade.account][msg.sender], "unauthorized"


    Vault(self.vault).remove_margin(trade.vault_position_uid, _amount)
```

and  the function close_position

```vyper
def close_trade(_trade_uid: bytes32, _min_amount_out: uint256) -> uint256:
    trade: Trade = self.open_trades[_trade_uid]
    assert (trade.account == msg.sender) or self.is_delegate[trade.account][msg.sender], "unauthorized"


    return self._full_close(trade, _min_amount_out)
```

above functions has the `trade.account == msg.sender` access control.

but when we look at the vault.vy , 

```vyper
def remove_margin(_position_uid: bytes32, _amount: uint256):
    """
    @notice
        Allows to remove margin from a Position and 
        increase the leverage.
    """
    assert self.is_whitelisted_dex[msg.sender], "unauthorized"


    position: Position = self.positions[_position_uid]


    assert position.margin_amount >= _amount, "not enough margin"
```

```vyper
def close_position(_position_uid: bytes32, _min_amount_out: uint256) -> uint256:
    assert self.is_whitelisted_dex[msg.sender], "unauthorized"
    return self._close_position(_position_uid, _min_amount_out)
```

above function only checks for is_whitelisted_dex. But they are external which can be called directly by a valid whitelisted dex who turned into malicious but still not removed from whitelisting.

We see there is function to remove whitelisting which we believe to remove any valid dex who turned into malicious.

## Impact

trading can be disrupted directly closing the position or removing the margin. this will deprive the valid trader.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L227-L229

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L528-L546

## Tool used

Manual Review

## Recommendation

1. add one more check such that only the `MarginDex` is the caller to these crucial functions.
