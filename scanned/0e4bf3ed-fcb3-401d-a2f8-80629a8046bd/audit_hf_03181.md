# [M] Template implementations doesn't validate configuration in initialize and update

## Summary
Severity: Medium
Contest weight: 0.2456
Dataset id: 17749
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In past audits, we have seen contract admins claim that invalidated configuration setters are fine since “admins are trustworthy”. However, cases such as Nomad got drained for over and Misconfiguration in the Acala stablecoin project allows attacker to steal 1.2 billion aUSD have shown again and again that even trustable entities can make mistakes. Thus any fields that might potentially result in insolvency of protocol should be thoroughly checked. NftPort template implementations often ignore checks for config fields. For the rest of the issue, we take royalty related fields as an example to illustrate potential consequences of misconfigurations. Notably, lack of check is not limited to royalty, but exists among most config fields. Admins are allowed to set a wrong royaltiesBps which is higher than ROYALTIES_BASIS. royaltyInfo() will accept this invalid royaltiesBps and users will pay a large amount of royalty. EIP-2981 (NFT Royalty Standard) defines royaltyInfo() function that specifies how much to pay for a given sale price. In general, royalty should not be higher than 100%. NFTCollection.sol checks that admins can't set royalties to more than 100%: /// Validate a runtime configuration change function _validateRuntimeConfig(RuntimeConfig calldata config) internal view { // Can't set royalties to more than 100% require(config.royaltiesBps <= ROYALTIES_BASIS, "Royalties too high"); ... But NFTCollection only check royaltiesBps when admins call updateConfig(), it doesn't check royaltiesBps in initialize() function, leading to admins could set an invalid royaltiesBps (higher than 100%) when initializing contracts. The same problem exists in ERC721NFTProduct and ERC1155NFTProduct. Both ERC721NFTProduct and ERC1155NFTProduct don't check royaltiesBasisPoints in initialize() function. Furthermore, these contracts also don't check royaltiesBasisPoints when admins call update() function. It means that admins could set an invalid royaltiesBasisPoints which may be higher than 100% in any time. EIP-2981 only defines royaltyInfo() that it should return royalty amount rather than royalty percentage. It means that if the contract has an invalid royalty percentage which is higher than 100%, royaltyInfo() doesn't revert and users will pay a large amount of royalty.

## Recommendation
Check royaltiesBps<=ROYALTIES_BASIS both in initialize() and update() functions.
