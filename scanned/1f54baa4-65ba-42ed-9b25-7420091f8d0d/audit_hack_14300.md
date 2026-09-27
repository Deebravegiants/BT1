# [M] The mint cap per address will not prevent a malicious user from minting most of the NFTs

## Summary
Severity: Medium
Reporter: twicek
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L143
Type: audit-issue

## Details
# The mint cap per address will not prevent a malicious user from minting most of the NFTs

## Summary
The mint cap per address does not fullfil its function of preventing users to mint more than 4 NFTs each.

## Vulnerability Detail
The following check is implemented in the `mint` function in an effort to prevent a unique user to mint most of the NFTs:

[MeritDutchAuction.sol#L143](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L143)
```solidity
		require(mintedPerAddressBefore + amount <= CAP_PER_ADDRESS, "Mint cap per address reached");
```

However, this check does not prevent a malicious user to create a contract that deploy any number of sub contract, each calling `mint`. Every sub contract would then send their 4 NFTs to the `tx.origin` EOA, leading to way more than 4 NFTs minted for this user. The whole operation being executed in one transaction.

This has actually already happened for the [Adidas NFT collection](https://nftevening.com/someone-sidestepped-adidas-nft-minting-terms-to-score-330-nfts/).


## Impact
Malicious users can buy most of the NFTs for a given auction which will limit the number of unique owner of this NFT collection to a few real users.

## Code Snippet
See above.

## Tool used

Manual Review

## Recommendation
Consider any of the mitigations mentioned in this [thread](https://twitter.com/Montana_Wong/status/1472302215880527872) from Montana Wong, each of them with their pros and cons.
