# [H] `Beebots.TradeValid`

## Summary
Severity: High
Contest weight: 0.3714
Dataset id: 265
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`Beebots.TradeValid()` will erroneously return true when `maker` is set to `address(0)` and `makerIds` are set to the `tokenIds` of unminted beebot NFTs.

`Beebots.verify()` returns true no matter what signature is given when signer is set to `address(0)`. This means that `BeeBots.tradeValid()` will erroneously return true when `maker` is set to `address(0)`.

Finally, before an NFT has even been minted at all, it is assumed to have an owner of `address(0)` due to the `idToOwner` mapping being initialized to zero for all uninitialized slots, so an attacker can call `tradeValid()` with `maker` set to `address(0)` and `makerIds` set to the `tokenIds` of any unminted `nftIds`, and `tradeValid()` will erroneously return true.

  * (1) `Beebots.verify()` returns true no matter what signature is given when signer is set to `address(0)`.

    * (1a) `BeeBots.verify()` does not check to ensure that signer is not `address(0)`.
    * (1b) This is a problem because `ecrecover` fails silently if the signature does not match and returns zero.
    * (1c) So if an attacker passes in `address(0)` as the signer, then verify will return true no matter what signature is provided, since `ecrecover` will return `address(0)`, and the signer is `address(0)`, so verify will pass.
    * (1d) This means that `BeeBots.tradeValid()` will erroneously return true when maker is set to `address(0)`.
  * (2) Before an NFT has even been minted at all, it is assumed to have an owner of `address(0)` due to the `idToOwner` mapping being initialized to zero for all uninitialized slots

    * (2a) Solidity initializes all mappings to 0 for all slots that have not yet been set.
    * (2b) So for any NFT ID that has not yet been minted, the corresponding owner in the mapping `BeeBots.idToOwner` is `address(0)`, even though that NFT should not even exist.
    * (2c) This means that an attacker can call `tradeValid()` with maker set to `address(0)` and makerIds set to any unminted nftIds, and `tradeValid()` will erroneously return true.

(1) Recommend adding this check to `Beebots.verify()`: `require(signer != address(0), "Cannot verify signatures from 0x0");`

(2) Recommend adding this check to `Beebots.tradeValid()`: `require(maker != address(0), "Maker 0x0 not allowed");`

Wow, this exploit is absolutely stunning.

## Recommendation
No recommendation
