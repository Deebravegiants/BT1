# [H] CAP_PER_ADDRESS could be easily bypassed

## Summary
Severity: High
Reporter: whiteh4t9527
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L143
Type: audit-issue

## Details
# CAP_PER_ADDRESS could be easily bypassed

## Summary
If an user can generate lots of EOAs or using a smart contract to generate lots of sub-contracts, he/she can easily bypass the CAP_PER_ADDRESS restriction and `mint()` as many NFTs as he/she wants.

## Vulnerability Detail
The [`CAP_PER_ADDRESS check`](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L143) uses the `mintedPerAddress[]` mapping to check if `msg.sender` reaches the cap of minting NFTs (i.e., `CAP_PER_ADDRESS`). However, by generating lots of EOA addresses, the restriction would be bypassed easily. Moreover, if an user deploys a smart contract and `new` lots of sub contracts as follows, he/she can `mint()` as many NFTs as possible in one transaction:

```solidity
contract Lib {
  constructor() payable {
    MeritDutchAuction.mint{value: msg.value}(1);
  }
}

contract Exp {
  function trigger(uint amount) payable {
    uint price = MeritDutchAuction.getPrice();
    for(uint i ; i<amount ; i++) {
      new Lib{value: price}();
    }
  }
}
```

## Impact
CAP_PER_ADDRESS check could be bypassed.

## Code Snippet
```solidity
    function mint(uint256 amount) external payable {
        // Checks
        // Cache mintedBefore to save on sloads
        uint256 mintedBefore = minted;
        // Cache mintedPerAddressBefore to save on sloads
        uint256 mintedPerAddressBefore = mintedPerAddress[msg.sender];
        // Price being paid is the current price
        uint256 pricePaid = getPrice();
        // Total price being paid is the current price times the amount of NFTs
        uint256 totalPaid = pricePaid * amount;
        // Auction must have started
        require(block.timestamp >= startTime, "Auction not started");
        // Cannot mint more than the mint cap
        require(mintedBefore + amount <= MINT_CAP, "Mint cap reached");
        // Cannot mint more than the cap per address
        require(mintedPerAddressBefore + amount <= CAP_PER_ADDRESS, "Mint cap per address reached");
```

## Tool used

Manual Review

## Recommendation
Use a whitelist mechanism to ensure the number of NFT to be minted by each user.
