# [M] Honest user may not get a fair chance to buy the NFTs

## Summary
Severity: Medium
Reporter: Juntao
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169
Type: audit-issue

## Details
# Honest user may not get a fair chance to buy the NFTs

## Summary

Honest user may not get a fair chance to buy the NFTs.

## Vulnerability Detail

When user calls [mint(...)](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169) method, protocol will first check if [CAP_PER_ADDRESS](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L12) will be exceed and revert if so:
```solidity
        uint256 mintedPerAddressBefore = mintedPerAddress[msg.sender];
        ...
        require(mintedPerAddressBefore + amount <= CAP_PER_ADDRESS, "Mint cap per address reached");
```
The purpose is to limit the number of purchases and ensure popular NFTs won't be bought out by few users very soon. However, there are ways to bypass the limitation and a single user can buy more than much more NFTs:

1. User can simply deploy serveral contracts and call each contract to buy 4 NFTs, ends up buying much more;
2. User can also call `mint(...)` from a contract with more eth than required, as the unused ether will be sent back to the contract,  the contract can deploy a new contract in **receive()** or **fallback()** method,  then mint again from the new deployed contract by reentering `mint(...)`.

***Please note this is different from a regular mint by using multiple accounts.**

This does not require user to pay more gas fee to front-run everytime, the costs are relatively low and chances are high, as the exploit can be done in one single transaction and user only needs to front-run successfully just once.

## Impact

Fairness is undermined.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169

## Tool used

Manual Review

## Recommendation

1. Add reentrancy protection to `mint(...)` method:

```diff
+   bool flag;

    function mint(uint256 amount) external payable {
+       require(!flag);
+       flag = true;

        ...

+       flag = false;
    }
```

2. Use **tx.origin** instead of msg.sender, this is to prevent user from minting more than 4 NFTs in a single transaction even if multiple accounts are used, so each user get a fair chance to buy the NFTs:

```diff
    function mint(uint256 amount) external payable {
       ...

        // Cache mintedPerAddressBefore to save on sloads
-       uint256 mintedPerAddressBefore = mintedPerAddress[msg.sender];
+       uint256 mintedPerAddressBefore = mintedPerAddress[tx.origin];

       ...

-       mintedPerAddress[msg.sender] += amount;
+       mintedPerAddress[tx.origin] += amount;

       ...
    }
```
