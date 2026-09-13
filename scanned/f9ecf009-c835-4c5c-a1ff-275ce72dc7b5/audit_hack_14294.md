# [H] Potential Sybil attack in NFT `mint`

## Summary
Severity: High
Reporter: 0x4non
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169
Type: audit-issue

## Details
# Potential Sybil attack in NFT `mint`

## Summary

The `mint` function in the `MeritDutchAuction` potentially allows for a Sybil attack. A user could create multiple accounts (or deploy multiple contracts) to mint NFTs and then transfer all the tokens to a single account, bypassing the per-address mint cap.

## Vulnerability Detail

The contract checks for a `CAP_PER_ADDRESS` which limits the amount of NFTs that can be minted by a single address. However, there are no measures in place to prevent an attacker from creating multiple addresses, each of which would then mint up to the cap, and then transferring all minted tokens to one single address. 

Similarly, a malicious user could create a smart contract that in turn deploys new contracts, each of which mints NFTs and subsequently transfers them back to the user's wallet. 

## Impact

The vulnerability potentially allows a malicious user to accumulate more NFTs than intended by the developers, which can impact the distribution and scarcity of the NFTs, and as a result, potentially their value.

## Code Snippet

[MeritDutchAuction.sol#L128-L169](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169)
```solidity
function mint(uint256 amount) external payable {
    ...
    require(mintedPerAddressBefore + amount <= CAP_PER_ADDRESS, "Mint cap per address reached");
    ...
    for(uint256 i = 0; i < amount; i++) {
        // Mint the amount of NFTs to the sender
        nft.mint(mintedBefore + i + 1, msg.sender);
    }
    ...
}
```

## Tool used

Manual Review

## Recommendation

One way to mitigate this is by using a whitelisting mechanism where only pre-approved addresses are allowed to call the mint function. This would make it much harder for an attacker to exploit the contract by using multiple addresses. This could be implemented in a simple way by adding a `whitelisted` mapping and a `onlyWhitelisted` modifier to the contract:

```solidity
mapping(address => bool) public whitelisted;

modifier onlyWhitelisted {
    require(whitelisted[msg.sender], "Not whitelisted");
    _;
}

function mint(uint256 amount) external payable onlyWhitelisted {
    ...
}

function addBuyer(address buyer) onlyOwner external {
    whitelisted[buyer] = true;
}
```

An alternative approach could involve implementing an on-chain identity verification mechanism to ensure that each address is linked to a unique individual or entity, although such a system could be complex to implement and may raise privacy concerns.
