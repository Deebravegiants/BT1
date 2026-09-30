# [M] `mintedPerAddress` limit can be bypassed atomically

## Summary
Severity: Medium
Reporter: 0xDjango
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L151C9-L151C48
Type: audit-issue

## Details
# `mintedPerAddress` limit can be bypassed atomically

## Summary
Beam implements a `mintedPerAddress` mapping to ensure that an address can only mint up to 4 NFTs. The check uses `msg.sender` for the call to the `mint()` function. This limit can easily be bypassed to mint as many NFTs as desired within a single atomic transaction.

## Vulnerability Detail
The `mint()` function checks that `msg.sender` can only mint up to 4 NFTs through the following lines of code:

```solidity
uint256 mintedPerAddressBefore = mintedPerAddress[msg.sender];
require(mintedPerAddressBefore + amount <= CAP_PER_ADDRESS, "Mint cap per address reached");
mintedPerAddress[msg.sender] += amount;
```

Since the checks use `msg.sender`, a single contract can mint as many NFTs as desired by:

1) Deploying multiple contracts that call `mint()`
2) Calling these contracts in a single transaction

***An example contract that can mint 20 NFTs in a single transaction:***

**Minter.sol**:
```solidity
contract Minter {
    // Minter aggregator contract
    address immutable aggregator = 0xExample;

    function callMint() external payable {
        MeritDutchAuction.mint(4); // Mint 4 NFTs from the Merit Dutch Auction
        MeritNFT.transfer(aggregator); // Transfer them to master aggregator contract
    }
}
```

**Aggregator.sol**:
```solidity
contract Aggregator {
    // Array of deployed minter contracts (pseudocode)
   address[] public minterContracts = [0xMinter0, 0xMinter1, 0xMinter2, 0xMInter3, 0xMinter4]

   function mintAll() external payable {
      for (uint i; i < minterContracts.length; ++i) {
          minterContracts[i].callMint(); // Loop through each contract and mint 4 NFTs each. 5 contracts * 4 NFTs = 20 NFTs
      }
   }
}
```

## Impact
- A single transaction can mint as many NFTs as desired, bypassing `mintedPerAddress` limit.
- Users will not have a fair chance to acquire NFTs.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L151C9-L151C48

## Tool used
Manual Review

## Recommendation
Use `txn.origin` instead of `msg.sender`. This will ensure that a single transaction can **only mint 4 NFTs** as is desired. Other users will have a fair chance to purchase their own NFTs.
