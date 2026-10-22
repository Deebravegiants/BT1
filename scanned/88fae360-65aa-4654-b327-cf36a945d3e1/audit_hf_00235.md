# [H] BasePool.mint

## Summary
Severity: High
Contest weight: 0.3537
Dataset id: 1206
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the contract BasePool the mint function can be frontrun. This will assign the NFT to the attacker which later on he can burn it retrieving the corresponding `_nativeAsset` and `_foreignAsset` initially deposited by the frontrun victim. <https://github.com/code-423n4/2021-11-vader/blob/main/contracts/dex/pool/BasePool.sol#L149-L194>

## Proof of Concept
User1 transfers 1000 `_nativeAsset` tokens and 1000 `_foreignAsset` tokens into the BasePool contract. User1 calls the `BasePool.mint()` function to retrieve his NFT. Attacker is constantly polling for an increase of the balance of `_nativeAsset` and `_foreignAsset` of the contract OR attacker is constantly scanning the mempool for `mint()` function calls. Attacker detects an increase of balance of `_nativeAsset` and `_foreignAsset` OR attacker detects a `mint()` function call in the mempool. Attacker frontruns the mint call and retrieves the NFT. Gets a NFT that is worth 1000 `_nativeAssets` and 1000 `_foreignAssets`. User1 gets a NFT that is worth 0 `_nativeAssets` and 0 `_foreignAssets`. Attacker burns the NFT retrieving the corresponding `_nativeAsset` and `_foreignAsset` initially deposited by the victim.

## Recommendation
Include in the `mint()` function the transfer of `_nativeAssets` and `_foreignAssets` to the smart contract.

The pool is meant to be utilized via the router or smart contracts and is not meant to be utilized directly. The exact same “flaw” exists in Uniswap V2 whereby if you transfer assets directly someone else can claim them on your behalf.

Ah, so this how you prevent direct access to the pools. The issue is valid due to lack of documentation on the usage of the router.

Firstly, documentation related issues cannot constitute a high risk vulnerability. Secondly, this type of documentation does not exist in Uniswap V2 either. We advise this finding to be set to no risk.
