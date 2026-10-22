# [M] M-03 | Address Initialization Allows Pools To Accumulate NFTs

## Summary
Severity: Medium
Contest weight: 0.1874
Dataset id: 21305
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Upon the first interaction with an address the address data flags are initialized, checking to see if the address holds any bytecode. If the account does not hold any bytecode at the time of account initialization then it receives only the _ADDRESS_DATA_INITIALIZED_FLAG flag. However if the address is later deployed to (e.g. a new pool is created at this address), the contract will not be excluded from ERC721 minting, as it will not automatically receive the _ADDRESS_DATA_SKIP_NFT_FLAG flag. As a result malicious actors may transfer tokens to an address where a pool for the token is about to be deployed to in order to avoid getting the address marked with the _ADDRESS_DATA_SKIP_NFT_FLAG. NFTs will then errantly be minted to and burned from the pool address upon liquidity modification and swaps. This creates a pool of NFTs which are not owned by end users, but instead locked up in a swap pool where a significant amount of them may not be able to move due to locked liquidity. In the case of a swap pool it would be possible for a flashloan to rescue potentially rare ERC721 tokens, however in the case of a locking contract or some other arbitrary integration these ERC721 tokens could be unintentionally locked for a significant amount of time.

## Recommendation
Consider checking whether an account houses bytecode when reading the getSkipNFT function, regardless of if the account has been initialized or not. Otherwise be sure to document this risk to users of DN404, advising them to implement their own _getSkipNFT functions or adding their own functionality for trusted addresses to mark addresses with the _ADDRESS_DATA_SKIP_NFT_FLAG as needed.
