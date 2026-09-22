# [H] __init__ function miss access control

## Summary
Severity: High
Reporter: mgf15
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L103-L128
Type: audit-issue

## Details
# __init__ function miss access control

## Summary
__init__ function miss an access control , and anyone can re-initialize the contract .
## Vulnerability Detail
the function 
```vy
def __init__(
    _weth_address: address,
    _nft_address: address,
    _start_token_id: uint256,
    _max_token_id: uint256,
    _reserve_price: uint256,
    _fallback_receiver: address,
    _vault_address: address
):
```
is missing access control and can be called by any one , the initialize must be once and only by the contract deployer . 
## Impact
attacker can initialize the contract and take the ownership .
## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L103-L128
```vy
def __init__(
    _weth_address: address,
    _nft_address: address,
    _start_token_id: uint256,
    _max_token_id: uint256,
    _reserve_price: uint256,
    _fallback_receiver: address,
    _vault_address: address
):
    assert _weth_address != empty(address), "invalid weth address"
    assert _nft_address != empty(address), "invalid nft address"
    assert _start_token_id < _max_token_id, "invalid token ids"
    assert _reserve_price > 0, "reserve price cannot be zero"
    assert _fallback_receiver != empty(address), "invalid fallback receiver address"
    assert _vault_address != empty(address), "invalid vault address"


    WETH = _weth_address
    NFT = _nft_address
    self.vault = _vault_address
    RESERVE_PRICE = _reserve_price
    FALLBACK_RECEIVER = _fallback_receiver


    self.owner = msg.sender


    self.current_epoch_token_id = _start_token_id
    self.max_token_id = _max_token_id
```
## Tool used

Manual Review

## Recommendation
check who can call this function and def __init__() must run once !
