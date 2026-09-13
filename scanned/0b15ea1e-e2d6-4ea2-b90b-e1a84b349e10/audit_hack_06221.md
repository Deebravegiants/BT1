# [H] withdraw_underlying_to_claim() allows anyone to call it resulting in  that  all shares in the protocol  can be burned , and the user profits by claiming

## Summary
Severity: High
Reporter: Bauer
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L394-L404
Type: audit-issue

## Details
# withdraw_underlying_to_claim() allows anyone to call it resulting in  that  all shares in the protocol  can be burned , and the user profits by claiming

## Summary
withdraw_underlying_to_claim() allows anyone to call it, the user can first call this function to increase the value of per share, and then call claim to profit with his share*per share.

## Vulnerability Detail
```vyper
def withdraw_underlying_to_claim(_amount_shares: uint256, _min_weth_out: uint256):
    """
    @notice
        Withdraws _amount_shares and _min_weth_out from Alchemix to be distributed
        to token holders.
        The WETH is held in this contract until it is `claim`ed.
    """
    amount_withdrawn: uint256 = self._withdraw_underlying_from_alchemix(_amount_shares, self, _min_weth_out)
    self._mark_as_claimable(amount_withdrawn)

    log Claimable(amount_withdrawn)
```
The function ```withdraw_underlying_to_claim()``` is used to withdraw WETH from Alchemix to be distributed. As the code above , anyone can call this function and specify the share balance of vault in the parameter.

```vyper
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
    position.amount_claimed += amount
    self.positions[_token_id] = position
    
    ERC20(WETH).transfer(token_owner, amount)

    log Claimed(_token_id, token_owner, amount)
    return amount

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
The Function ```claim()``` allows a token holder to claim his share of pending WETH. The amount to be claimed is obtained from this function ```_claimable_for_token()``` . The pending WETH for a given token_id is  calculated according to this formula ``` position.shares_owned * self.amount_claimable_per_share / PRECISION```. If ```amount_claimable_per_share``` is larger, the result will be larger. The more token the user gets.

```vyper
def _mark_as_claimable(_amount: uint256):
    """
    @notice
        Marks _amount of WETH as claimable by token holders and
        calculates the amount_claimable_per_share.
    """
    if _amount == 0 or self.total_shares == 0:
        return

    assert ERC20(WETH).balanceOf(self) >= _amount

    self.amount_claimable_per_share += _amount * PRECISION / self.total_shares

```
Howver , the ```amount_claimable_per_share ``` is calculated according to this formula ```amount_claimable_per_share += _amount * PRECISION / self.total_shares``` in the function ```_mark_as_claimable()``` and the function ```_mark_as_claimable()``` is used in the function ```withdraw_underlying_to_claim()```.  The larger ```_amount``` is, the larger the per share will be. If the user calls function ``` withdraw_underlying_to_claim()```   before calim and specify the share balance of vault in the parameter  , the final calculated per share will be the largest, and the user will get more weth after cliam.


## Impact
All shares will be burned and the assets in the protocol will be lost

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L394-L404

## Tool used

Manual Review

## Recommendation
```vyper

add assert self.is_operator[msg.sender], "not allowed" 
def withdraw_underlying_to_claim(_amount_shares: uint256, _min_weth_out: uint256):
    """
    @notice
        Withdraws _amount_shares and _min_weth_out from Alchemix to be distributed
        to token holders.
        The WETH is held in this contract until it is `claim`ed.
    """
    assert self.is_operator[msg.sender], "not allowed"
    amount_withdrawn: uint256 = self._withdraw_underlying_from_alchemix(_amount_shares, self, _min_weth_out)
    self._mark_as_claimable(amount_withdrawn)

    log Claimable(amount_withdrawn)

```
