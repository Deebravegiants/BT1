# [M] M-02 | Delegation Is Broken For Punks

## Summary
Severity: Medium
Contest weight: 0.1332
Dataset id: 2087
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Try
IExclusiveDelegateResolver(EXCLUSIVE_DELEGATE_RESOLVER_ADDRESS).exclusiveOwnerByRights(shadowCollectionAddress, tokenId, SHADOW_TOKEN_RIGHTS
The logic attempts to ﬁnd the owner via the exclusive delegate resolver, However we are using the
punk adapter address (shadowCollectionAddress) instead of the punk721 address to ﬁnd the owner.
This will result in delegated wallets not being able to mint a shadow nft.
The functionality of the contract should allow non locked nft to mint shadow NFT’s using the
delegation functionality, however since we query the wrong address in the delegate resolver, it is not
possible to retrieve the delegated user via the beacon contract.
Given that users usually hold punks in cold wallets and use delegations to the hot wallet, this will
limit the functionality of shadow nfts as they cannot be minted to delegated wallet addresses of the
punk holders.

## Recommendation
If the address is the punk adapter, use the punks721 address when querying the delegate resolver.
