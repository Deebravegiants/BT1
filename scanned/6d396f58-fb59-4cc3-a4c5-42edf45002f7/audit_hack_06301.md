# [H] [H] Newly created positions can claim old claimable

## Summary
Severity: High
Reporter: oxcm
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L428-L440
Type: audit-issue

## Details
# [H] Newly created positions can claim old claimable

## Summary

Newly created positions have a default value of `0` for `amount_claimed`, lead to an immediate value in `_claimable_for_token()`, that should be `0`.

## Vulnerability Detail

The `_claimable_for_token()` function is responsible for calculating the pending WETH for a given token_id. 

When a new position is created, its `amount_claimed` default value is `0`, If the `amount_claimable_per_share` has a value, then the `_claimable_for_token` function of the new position will immediately have a value. 

This is because the calculation of `_claimable_for_token` is based on `total_claimable_for_position` - `position.amount_claimed`, where `total_claimable_for_position` is derived from the multiplication of the `shares_owned` of the position and the current `amount_claimable_per_share`. As the `shares_owned` of the new position are not zero, the `_claimable_for_token` will have a value immediately.


## Impact

if a new position owner claims this amount, the protocol will not have enough funds to pay the original investors' rewards, and some claim transactions will fail due to insufficient funds.

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L428-L440

```vyper=428
@view
@internal
def _claimable_for_token(_token_id: uint256) -> uint256:
    """
    @notice
        Calculates the pending WETH for a given token_id.
    """
    position: Position = self.positions[_token_id]
    if position.is_liquidated:
        return 0
    
    total_claimable_for_position: uint256 = position.shares_owned * self.amount_claimable_per_share / PRECISION
    return total_claimable_for_position - position.amount_claimed
```

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L198-L232

```vyper=198
@nonreentrant("lock")
@external
def register_deposit(_token_id: uint256, _amount: uint256):
    """
    @notice
        Registers a new deposit of _amount for _token_id.
        _amount WETH is deposited into Alchemix and a corresponding
        loan is taken out and sent to fund_receiver.
    """
    assert self.is_depositor[msg.sender], "not allowed"
    assert self._is_valid_token_id(_token_id)

    position: Position = self.positions[_token_id]
    assert position.is_liquidated == False, "position already liquidated"

    position.token_id = _token_id
    position.amount_deposited += _amount

    # transfer WETH to self
    ERC20(WETH).transferFrom(msg.sender, self, _amount)

    # deposit WETH to Alchemix
    shares_issued: uint256 = self._deposit_to_alchemist(_amount)
    position.shares_owned += shares_issued
    self.total_shares += shares_issued
    
    self.positions[_token_id] = position

    # mint alchemix debt to fund_receiver
    amount_to_mint: uint256 = self._calculate_amount_to_mint(shares_issued)
    assert amount_to_mint > 0, "cannot mint new Alchemix debt"

    self._mint_from_alchemix(amount_to_mint, self.fund_receiver)

    log Deposit(msg.sender, _token_id, _amount)
```

## Tool used

Manual Review / ChatGPT PLUS


## Recommendation

One possible solution is to add a new storage variable `last_amount_claimable_per_share` in the Position.

Then, in the `register_deposit` function, check if `position.last_amount_claimable_per_share` is `0`. If so, set `position.last_amount_claimable_per_share` to `self.amount_claimable_per_share`. 

Finally, modify the `_claimable_for_token` function.

The modified code snippets for these changes are as follows:

```vyper
struct Position:
    token_id: uint256
    amount_deposited: uint256
    shares_owned: uint256
    amount_claimed: uint256
    is_liquidated: bool
    last_amount_claimable_per_share: uint256  # new storage variable

@view
@internal
def _claimable_for_token(_token_id: uint256) -> uint256:
    """
    @notice
        Calculates the pending WETH for a given token_id.
    """
    position: Position = self.positions[_token_id]
    if position.is_liquidated:
        return 0

    diff_claimable_per_share = self.amount_claimable_per_share - position.last_amount_claimable_per_share
    total_claimable_for_position: uint256 = position.shares_owned * diff_claimable_per_share / PRECISION  # calculate claimable based on the difference between current and last amounts
    return total_claimable_for_position

@external
def claim(_token_id: uint256) -> uint256:
    """
    @notice
        Allows a token holder to claim his share of pending WETH.
    """
    token_owner: address = ERC721(NFT).ownerOf(_token_id)
    assert msg.sender == token_owner, "only token owner can claim"

    amount: uint256 = self._claimable_for_token(_token_id)
    assert amount > 0, "nothing to claim"

    position: Position = self.positions[_token_id]
    position.last_amount_claimable_per_share = self.amount_claimable_per_share
    self.positions[_token_id] = position
    
    ERC20(WETH).transfer(token_owner, amount)

    log Claimed(_token_id, token_owner, amount)
    return amount

@external
def register_deposit(_token_id: uint256, _amount: uint256):
    """
    @notice
        Registers a new deposit of _amount for _token_id.
        _amount WETH is deposited into Alchemix and a corresponding
        loan is taken out and sent to fund_receiver.
    """
    assert self.is_depositor[msg.sender], "not allowed"
    assert self._is_valid_token_id(_token_id)

    position: Position = self.positions[_token_id]
    assert position.is_liquidated == False, "position already liquidated"

    position.token_id = _token_id
    position.amount_deposited += _amount

    # transfer WETH to self
    ERC20(WETH).transferFrom(msg.sender, self, _amount)

    # deposit WETH to Alchemix
    shares_issued: uint256 = self._deposit_to_alchemist(_amount)
    position.shares_owned += shares_issued
    self.total_shares += shares_issued

    # update last amount claimable per share for the position
    if position.last_amount_claimable_per_share == 0:
        position.last_amount_claimable_per_share = self.amount_claimable_per_share

    self.positions[_token_id] = position

    # mint alchemix debt to fund_receiver
    amount_to_mint: uint256 = self._calculate_amount_to_mint(shares_issued)
    assert amount_to_mint > 0, "cannot mint new Alchemix debt"

    self._mint_from_alchemix(amount_to_mint, self.fund_receiver)

    log Deposit(msg.sender, _token_id,

```
