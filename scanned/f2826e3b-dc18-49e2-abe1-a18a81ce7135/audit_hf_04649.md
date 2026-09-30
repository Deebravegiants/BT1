# [H] CouncilMember:burn renders the contract inoperable due to misaligned balances array

## Summary
Severity: High
Contest weight: 0.7862
Dataset id: 22388
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The CouncilMember contract suffers from a critical vulnerability that misaligns the balances array after a successful burn, rendering the contract inoperable.  
The root cause of the vulnerability is that the burn function incorrectly manages the balances array, shortening it by one each time an ERC721 token is burned while the latest minted NFT still withholds its unique tokenId which maps to the previous value of balances.length.  
210:  
```solidity
function burn(
...
220:
balances.pop(); // <= FOUND: balances.length decreases, while latest minted nft withold its unique tokenId
221:
_burn(tokenId);
222:
}
```
This misalignment between existing tokenIds and the balances array results in several critical impacts:  
1. Holders with tokenId greater than the length of balances cannot claim.  
2. Subsequent burns of tokenId greater than balances length will revert.  
3. Subsequent mint operations will revert due to tokenId collision. As totalSupply now collides with the existing tokenId.  
173:  
```solidity
function mint(
...
179:
180:
balances.push(0);
181:
_mint(newMember, totalSupply());// <= FOUND
182:
}
```
This mismanagement creates a cascading effect, collectively rendering the contract inoperable. Following POC will demonstrate the issue more clearly in codes.  
The severity of the vulnerability is high due to the high likelihood of occurence and the critical impacts on the contract's operability and token holders' ability to interact with their assets.

## Proof of Concept
Run git apply on the following patch then run npx hardhat test to run the POC.  
Result  
CouncilMember mutative burn Success inoperable contract after burn (90ms) 1 passing (888ms)  
The Passing execution of the POC confirmed that operations such as claim, burn & mint were all reverted which make the contract inoperable.

## Recommendation
It is recommended to avoid popping out balances to keep alignment with uniquely minted tokenId. Alternatively, consider migrating to ERC1155, which inherently manages a built-in balance for each NFT.
