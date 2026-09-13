# [C] Anybody can mint DebtToken

## Summary
Severity: Critical
Source: https://github.com/dharmaprotocol/charta/blob/b110959477cf37375bf7e9344d40eb85219c8575/contracts/DebtToken.sol
Type: audit-issue

## Details
[DebtToken](https://github.com/dharmaprotocol/charta/blob/b110959477cf37375bf7e9344d40eb85219c8575/contracts/DebtToken.sol) extends [MintableNonFungibleToken](https://github.com/dharmaprotocol/NonFungibleToken/blob/master/contracts/MintableNonFungibleToken.sol) and thus inherits a public [mint](https://github.com/dharmaprotocol/NonFungibleToken/blob/master/contracts/MintableNonFungibleToken.sol#L23) function that allows the caller to create new tokens.

Given that there is an additional [create](https://github.com/dharmaprotocol/charta/blob/b110959477cf37375bf7e9344d40eb85219c8575/contracts/DebtToken.sol#L61) function defined in `DebtToken` which requires authorization, it’s clear to us that `mint` should require the same. Otherwise, it can be called by anyone with an arbitrary token id.

A consequence of this function being public is that anyone is able to impede the filling of a debt order, by minting a token with the corresponding issuance hash as _id_ before the order is attempted to be filled. The entire system can be put to a halt in this way.

To fix this, add to `mint` the same [authorization check](https://github.com/dharmaprotocol/charta/blob/b110959477cf37375bf7e9344d40eb85219c8575/contracts/DebtToken.sol#L75) seen in`create`.

_**Update:** Fixed in [97690a9](https://github.com/dharmaprotocol/NonFungibleToken/commit/97690a94416f841d6b69d33cf1d764a09b5d5f0b) by making `mint` an internal function in `MintableNonFungibleToken`._
