# [M] No address check before transffering NFT

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-astaria
Published: 2022-11-07
Source: https://github.com/sherlock-audit/2022-10-astaria-judging/issues/288
Type: sherlock-finding

## Details
Rohan16

medium

# No address check before transffering NFT

## Summary
NFT tranfered to market directly can be took by anyone
## Vulnerability Detail

1. Offer can be made on any NFT if:
     - Not in active auction
     - No existing offer
     - The new offer amount is greater than existing offer

## Impact
Before transferring the NFT their should be a address check which is highly important to check 
Impact can be seen through here,
https://github.dev/sherlock-audit/2022-10-astaria/blob/main/src/CollateralToken.sol#L176
## Code Snippet
```solidity
 function flashAction(
    IFlashAction receiver,
    uint256 collateralId,
    bytes calldata data
  ) external onlyOwner(collateralId) {
    address addr;
    uint256 tokenId;
    (addr, tokenId) = getUnderlying(collateralId);
    IERC721 nft = IERC721(addr);

    bytes memory preTransferState;
    //look to see if we have a security handler for this asset

    if (securityHooks[addr] != address(0)) {
      preTransferState = ISecurityHook(securityHooks[addr]).getState(
        addr,
        tokenId
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-astaria-judging/issues/288_
