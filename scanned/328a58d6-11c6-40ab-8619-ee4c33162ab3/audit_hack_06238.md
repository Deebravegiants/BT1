# [M] `is_operator`architecture is wrong

## Summary
Severity: Medium
Reporter: 0xSmartContract
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L631-L642
Type: audit-issue

## Details
# `is_operator`architecture is wrong

## Summary

`is_operator` has problems in mapping architecture design in the following detail,
`is_operator` Although there is a risk of centrality, it has been evaluated out of centrality due to the authorization of the newly defined operators and the invalidity of the contract.


## Vulnerability Detail

`is_operator` is hashMap for operators register.

First defined initially as state variable;

```vyper
contracts/Vault.vy:
  141: is_operator: public(HashMap[address, bool])
```


At this point , first operator is defined in `__init__` function with msg.sender;

```vyper
contracts/Vault.vy:
  213  @external
  214: def __init__(
  215:     _nft_address: address,
  216: ):
  217:     assert _nft_address != empty(address), "invalid nft address"
  218:     NFT = _nft_address
  219: 
  220:     self.is_operator[msg.sender] = True
```

Operators can be defined with `add_operator`, operators can be removed with `remove_operator`;

```vyper
contracts/Vault.vy:
  623  
  624: @external
  625: def add_operator(_new_operator: address):
  626:     """
  627:     @notice
  628:         Add a new address to the priviledged operators.
  629:     """
  630:     assert self.is_operator[msg.sender], "unauthorized"
  631:     assert self.is_operator[_new_operator] == False, "already operator"
  632: 
  633:     self.is_operator[_new_operator] = True
  634: 
  635:     log NewOperator(_new_operator, msg.sender)
  636: 
  637: 
  638: @external
  639: def remove_operator(_to_remove: address):
  640:     """
  641:     @notice
  642:         Remove an existing operator from the priviledged addresses.
  643:     """
  644:     assert self.is_operator[msg.sender], "unauthorized"
  645:     assert self.is_operator[_to_remove], "not an operator"
  646: 
  647:     self.is_operator[_to_remove] = False
  648: 
  649:     log OperatorRemoved(_to_remove, msg.sender)

```

This architecture has some problem for contract actions;

1) `is_operator` can define itself as msg.sender at the beginning, then remove it with `remove_operator` and in such case no important functions can be used in the project
Functions that cannot be used in this case;
`def add_depositor()`
`def remove_depositor()`
`def set_alchemist`
`def set_fund_receiver`
`def add_operator()`
`def remove_operator()`

2) `is_operator` can define itself as msg.sender at the beginning, then add a new operator with `add_operator` and remove the main operator defined in `__init__` with the newly added operator `remove_operator` (I don't think this is a desired architecture)



## Impact

```vyper
  638: @external
  639: def remove_operator(_to_remove: address):
  640:     """
  641:     @notice
  642:         Remove an existing operator from the priviledged addresses.
  643:     """
  644:     assert self.is_operator[msg.sender], "unauthorized"
  645:     assert self.is_operator[_to_remove], "not an operator"
  646: 
  647:     self.is_operator[_to_remove] = False
  648: 
  649:     log OperatorRemoved(_to_remove, msg.sender)

```

## Code Snippet
[Vault.vy#L631-L642](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L631-L642)

## Tool used

Manual Review

## Recommendation
```diff

+ is_main_operator: public(HashMap[address, bool])
is_operator: public(HashMap[address, bool])

  214: def __init__(
  215:     _nft_address: address,
  216: ):
  217:     assert _nft_address != empty(address), "invalid nft address"
  218:     NFT = _nft_address
  219: 
+ 220:     self.is_main_operator[msg.sender] = True


  638: @external
  639: def remove_operator(_to_remove: address):
  640:     """
  641:     @notice
  642:         Remove an existing operator from the priviledged addresses.
  643:     """
  644:     assert self.is_operator[msg.sender], "unauthorized"
  645:     assert self.is_operator[_to_remove], "not an operator"
+             assert _to_remove != is_main_operator, "invalid remove address"
  646: 
  647:     self.is_operator[_to_remove] = False
  648: 
  649:     log OperatorRemoved(_to_remove, msg.sender)

```
