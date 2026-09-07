# [M] `reclaimErc721Tokens()` has no limit tokenAddress is nftContract address

## Summary
Severity: Medium
Chain: Smart contract
Component: SafeStaking-by-HOPR
Published: 2023-10-07
Source: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/18
Type: hats-finding

## Details
**Github username:** @9olidity
**Submission hash (on-chain):** 0x4be64e7eaf530282d270ffa85b7f513bcd962955e13aeb161a9619cb7a0d1d58
**Severity:** medium

**Description:**
**Description**\
`reclaimErc721Tokens()` has no limit tokenAddress is nftContract address

**Attack Scenario**\
In the `HoprStake.sol` contract `reclaimErc721Tokens` function, the administrator can enter any address. If the entered address is an `nftContract` address, then the administrator can take out the `nftContract` in the contract. Once nft is taken out, unlock will not be executed.

**Attachments**

1. **Proof of Concept (PoC) File**


2. **Revised Code File (Optional)**
```diff
  function reclaimErc721Tokens(address tokenAddress, uint256 tokenId) external onlyOwner nonReentrant {
+    require(tokenAddress != address(nftContract), 'HoprStake: Cannot claim HoprBoost NFT');
    IHoprBoost(tokenAddress).transferFrom(address(this), owner(), tokenId);
  }
```
