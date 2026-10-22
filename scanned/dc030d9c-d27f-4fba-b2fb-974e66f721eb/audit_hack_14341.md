# [M] Use `_safeMint` instead of `_mint` in MeritNFT contract

## Summary
Severity: Medium
Reporter: 0x4non
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L63
Type: audit-issue

## Details
# Use `_safeMint` instead of `_mint` in MeritNFT contract

## Summary

The mint function in the provided MeritNFT contract utilizes the `_mint()` function when the OpenZeppelin (OZ) contract advises the use of `_safeMint()` instead.

## Vulnerability Detail

The vulnerability arises from the fact that `_mint()` does not verify if the recipient is a contract, and whether that contract can correctly handle ERC721 tokens. If the recipient is a contract that cannot handle ERC721 tokens, tokens may be locked or lost.

This issue is addressed in the OpenZeppelin ERC721 documentation for the `_mint` method, where it is stated: "Usage of this method is discouraged, use _safeMint whenever possible".

## Impact

If the recipient of the minted token is a contract unable to handle ERC721 tokens, tokens may be irretrievably lost. This is a potential attack vector for malicious entities to exploit, and could result in users losing their assets.

## Code Snippet

[MeritNFT.sol#L61-L63](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L63)
```solidity
function mint(uint256 _tokenId, address _receiver) external onlyMinter {
    _mint(_receiver, _tokenId);
}
```

## Tool used

Manual Review

## Recommendation

Replace `_mint()` with `_safeMint()` in the `mint` function. This would look as follows:

```solidity
function mint(uint256 _tokenId, address _receiver) external onlyMinter {
    _safeMint(_receiver, _tokenId);
}
```

Take into consideration that `safeMint` will trigger a callback to the receiver, so it is crucial to adhere to the [Check-Effects-Interaction pattern](https://fravoll.github.io/solidity-patterns/checks_effects_interactions.html) to prevent potential re-entrancy attacks.
