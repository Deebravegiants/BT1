# [H] Lack of validation in the mint function assumes that MeritDutchAuction.sol#mint has passed for every iteration.

## Summary
Severity: High
Reporter: dopeflamingo
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156C1-L159
Type: audit-issue

## Details
# Lack of validation in the mint function assumes that MeritDutchAuction.sol#mint has passed for every iteration.

## Summary

The ```MeritDutchAuction.sol``` lacks proper validation for NFT minting, which can lead to an inconsistent state if the minting process fails for any reason. This vulnerability could result in incorrect incrementation of the ```minted``` and ```mintedPerAddress``` variables, leading to an inconsistent state. A potential attacker could exploit this vulnerability to manipulate the minting process and disrupt the integrity of the auction.

## Vulnerability Detail

The contract does not handle potential failures during the minting process, assuming that the NFT minting operation always succeeds. As a result, if the underlying NFT contract's ```mint``` function fails or throws an exception, it can lead to incorrect incrementation of minting-related variables, without minting the actual NFTs. This inconsistency can result in a misleading state of the contract and affect the fairness of the auction.

## Impact

If the minting process fails during execution, the contract's state becomes inconsistent, where the ```minted``` and ```mintedPerAddress``` variables are incremented without successfully minting the corresponding NFTs. This vulnerability can undermine the integrity of the auction and potentially enable attackers to exploit the inconsistent state for their advantage.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156C1-L159

## Tool used

Manual Review

## Recommendation
I recommend adding a try-catch system in order to ensure that the external call was successful or not and revert the whole transaction if not. 

```
function mint(uint256 amount) external payable {
    // ... existing code ...
    
    // Interactions
    for(uint256 i = 0; i < amount; i++) {
        try nft.mint(mintedBefore + i + 1, msg.sender) {
            // Minting successful, proceed to the next iteration
        } catch {
            // Minting failed, revert the transaction
            revert("NFT minting failed");
        }
    }

    // ... existing code ...
}
```

Alternatively change ```_mint``` function in ```MeritNFT.sol``` to ```_safeMint``` to ensure that the state of the contract is consistent.
