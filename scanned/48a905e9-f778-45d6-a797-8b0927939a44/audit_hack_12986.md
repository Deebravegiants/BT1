# [H] Everyone can close eachother positions in close_position vault.vy and BREAK the posations

## Summary
Severity: High
Reporter: Avci
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L225-L280
Type: audit-issue

## Details
# Everyone can close eachother positions in close_position vault.vy and BREAK the posations

## Summary
Everyone can close each other positions in close_position vault.vy
## Vulnerability Detail
in contract vault.vy:close_position is not checking the position `_position_uid` with the actual position owner thus bad actor can grief the users by setting a bot for closing everyone's position and make the positions unusable and break it. 

```vyper
@external
def close_position(_position_uid: bytes32, _min_amount_out: uint256) -> uint256:
    assert self.is_whitelisted_dex[msg.sender], "unauthorized"
    return self._close_position(_position_uid, _min_amount_out)



```
## Impact
bad actor can grief the users by setting a bot for closing everyone's position and make the positions unusable and break it. 
## Code Snippet
```vyper
@external
def close_position(_position_uid: bytes32, _min_amount_out: uint256) -> uint256:
    assert self.is_whitelisted_dex[msg.sender], "unauthorized"
    return self._close_position(_position_uid, _min_amount_out)

```
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L225-L280

## Tool used

Manual Review

## Recommendation
- consider using checks that checks the actual user who opened position and gives permission for only the position owner to close his positions
