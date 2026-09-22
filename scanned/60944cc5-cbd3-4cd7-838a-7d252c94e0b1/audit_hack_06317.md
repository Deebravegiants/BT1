# [M] The value of `_is_valid_token_id` in the `register_deposit()` function is unpredictable

## Summary
Severity: Medium
Reporter: 0xSmartContract
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L208
Type: audit-issue

## Details
# The value of `_is_valid_token_id` in the `register_deposit()` function is unpredictable

## Summary

One of the arguments in the `register_deposit()` function is `_is_valid_token_id`,  this is registers a new deposit of `_amount` for `_token_id`

but this argument is very hard to guess, because `_token_id` reverts to invalid ID in NFT contract, where there must be a mapping record to find valid ID


```vyper
ERC721(NFT).ownerOf(_token_id) # reverts for invalid token_id according to spec
```

## Vulnerability Detail

```vyper
contracts/Vault.vy:
  226  
  227: @nonreentrant("lock")
  228: @external
  229: def register_deposit(_token_id: uint256, _amount: uint256):
  242:     assert self.is_depositor[msg.sender], "not allowed"
  243:     assert self._is_valid_token_id(_token_id) # @audit how can user can be  token id?


contracts/Vault.vy:
  500  @internal
  501: def _is_valid_token_id(_token_id: uint256) -> bool:
  502:     """
  503:     @notice
  504:         Checks if the given _token_id exists.
  505:         Reverts if token isn't minted.
  506:     """
  507:     ERC721(NFT).ownerOf(_token_id) # reverts for invalid token_id according to spec
  508:     return True

```

## Impact

1) Alice wants to trade with the `register_deposit` function
2) Alice who does not know which _token_id to use in the ERC721(NFT) contract (there is no control or information she can know) cannot reach the unpredictable token_id


## Code Snippet

[Vault.vy#L208](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L208)

## Tool used

Manual Review

## Recommendation

Make sure the `_token_id` that needs to be used is tracked in a mapping and with the record in this mapping, the `register_deposit` function is called with the next id
