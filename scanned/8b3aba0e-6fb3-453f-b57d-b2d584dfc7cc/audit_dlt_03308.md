# [M] There is no re-register o re-assign function

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-canto
Published: 2022-11-28
Source: https://github.com/code-423n4/2022-11-canto-findings/issues/131
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-11-canto/blob/2733fdd1bee73a6871c6243f92a007a0b80e4c61/CIP-001/src/Turnstile.sol#L86-L101
https://github.com/code-423n4/2022-11-canto/blob/2733fdd1bee73a6871c6243f92a007a0b80e4c61/CIP-001/src/Turnstile.sol#L107-L120


# Vulnerability details

## Impact
There is no re-register or re-assign option for the smart contracts.

Let's assume a smart contract is registered either through the `register()` function with a new NFT minted or the `assign()` function to an existing NFT.
However, if somehow, the NFT is burned by the owner or transferred to another owner either by an approval or compromised tx, there is no option to re-register for these contracts which create gas fees but might not get a fee distribution in return. 

And if the NFT is burned or transferred to another owner, the smart contracts will lose the fees generated if not previously withdrawn.

## Proof of Concept
`register` function;
```solidity
    function register(address _recipient) public onlyUnregistered returns (uint256 tokenId) {
        address smartContract = msg.sender;

        if (_recipient == address(0)) revert InvalidRecipient();

        tokenId = _tokenIdTracker.current();
        _mint(_recipient, tokenId);
        _tokenIdTracker.increment();

        emit Register(smartContract, _recipient, tokenId);

        feeRecipient[smartContract] = NftData({
            tokenId: tokenId,
            registered: true
        });
    }
```
[Permalink](https://github.com/code-423n4/2022-11-canto/blob/2733fdd1bee73a6871c6243f92a007a0b80e4c61/CIP-001/src/Turnstile.sol#L86-L101)


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-11-canto-findings/issues/131_
