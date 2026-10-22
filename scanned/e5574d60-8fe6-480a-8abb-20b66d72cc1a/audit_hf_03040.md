# [M] Public to all funds escape

## Summary
Severity: Medium
Contest weight: 0.1798
Dataset id: 17046
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `LooksRareAggregator` smart contract implements a bunch of functions to escape funds by the contract owner (see `rescueETH`, `rescueERC20`, `rescueERC721`, and `rescueERC1155`). In this way, any funds that were accidentally sent to the contract or were locked due to incorrect contract implementation can be returned to the owner. However, locked funds can be rescued by anyone without the owner’s permission. This is completely contrary to the idea of having rescue functions.

In order to withdraw funds from the contract, a user may just call the `execute` function in the `ERC20EnabledLooksRareAggregator` with `tokenTransfers` that contains the addresses of tokens to be withdrawn. 

Thus, after the order execution `_returnERC20TokensIfAny` and `_returnETHIfAny` will be called, and the whole balance of provided ERC20 tokens and Ether will be returned to `msg.sender`.

Please note, that means that the owner can be front-ran with `rescue` functions and an attacker will receive funds instead.

Useless of rescue functionality and vulnerability to jamming funds.

## Recommendation
`_returnETHIfAny` and `_returnERC20TokensIfAny` should return the amount of the token that was deposited.

As only stuck funds are at risk, and as the aggregator contract itself is not supposed to handle funds, I don’t think this qualifies for High Severity.

We have decided that any ERC20 tokens sent there accidentally are free for all.

Keeping the Medium severity because the contract implements `TokenRescuer`, so the intent “that any ERC20 tokens sent there accidentally are free for all” totally makes sense but wasn’t clear prior to the audit. So I consider this a case where tokens that should belong to the protocol could be withdrawn by anyone.
