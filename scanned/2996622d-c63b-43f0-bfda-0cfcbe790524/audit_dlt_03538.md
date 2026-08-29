# [H] Users making specific chain account ownership upgrades will likely cause issues when later using cross-chain replay-able ownership upgrades

## Summary
Severity: High
Chain: Smart contract
Component: 2024-03-coinbase
Published: 2024-03-21
Source: https://github.com/code-423n4/2024-03-coinbase-findings/issues/114
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-03-coinbase/blob/main/src/SmartWallet/MultiOwnable.sol#L102


# Vulnerability details

**Impact**

Users are able to upgrade their account's owners via either directly onto the contract with a regular transaction or via an ERC-4337 EntryPoint transaction calling `executeWithoutChainIdValidation`. If a user chooses to use a combination of these methods it's very likely that the addresses at a particular ownership index differ across chain. Therefore if a user later calls `removeOwnerAtIndex` on another chain will end up removing different addresses on different chains. It is unlikely this would be the users intention. The severity of this ranges from minimal (the user can just add the mistakenly removed owner back) or criticial (the user mistakenly removes their only accessible owner on a specific chain, permanently locking the account).

**Proof Of Concept**

Scenario A: Alice permanently bricks her account on an unused chain:
1. Alice has a CoinbaseSmartWallet, and uses it on Base, Ethereum & Optimism.
2. Alice later decides to add a new owner using a cross-chain `executeWithoutChainIdValidation`
3. Alice later wants to remove the initial owner (index 0) and does so by signing another cross-chain replayable signature.
4. Despite it not being her intention anyone could take that signature and replay it on Arbitrum, Avalanche etc as there is no check to stop the user removing the final owner.

Scenario A: Alice adds owners using both methods and ends up with undesired results
1. Alice has a CoinbaseSmartWallet, and uses across all chains.
2. She has Gnosis Safe's and ERC-6551 token bound accounts on different chains so adds them as owners on those specific chains using `execute`.
3. She then adds a secondary EOA address on all chains using `executeWithoutChainIdValidation`
4. Now if she uses `executeWithoutChainIdValidation` to call `removeOwnerAtInde` she will be removing different owners on different chains, which is likely not her intention.

While more complex scenarios than this might sound bizarre it's important to remember that Alice could be using this smart account for the next N years, only making changes sporadically, and as her ownership mappings across different chains become more out of sync the likelihood of a signifanct error occuring increases.

**Recommended Mitigation**
As `MultiOwnableStorage` uses a mapping to track owner information rather than a conventional array, it might be simpler to do away with the indexes entirely and have a `removeOwner(bytes calldata _ownerToRemove)` function. This would avoid the sitations outlined above where when calling `removeOwnerAtIndex` removes different owners on different chains. To ensure replayability and avoid having a stuck nonce on chains where `_ownerToRemove` is not an owner the function should not revert in the case the owner is not there, but instead return a bool `removed` to indicate whether an owner was removed or not.

This would make it significantly less likely that users run into the issues stated above, without having to limit their freedom to make ownership changes manually or via ERC-4337 EntryPoint transactions.


## Assessed type

Other
