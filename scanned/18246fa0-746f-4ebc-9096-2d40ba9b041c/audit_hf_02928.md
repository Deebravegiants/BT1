# [H] spend/addXP will not add or spend correctly

## Summary
Severity: High
Contest weight: 0.7636
Dataset id: 16274
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Varonve.md Using spendXP as an example, the pattern in addXP but our recommendation there is to change the pattern, hence it applies more to spendXP: If the balance of the NFT is not enough just the balance of the NFT is removed, to prevent underflow:
```solidity
stakedNFTs[_address][i].balance = 0;
spent += stakedNFTs[_address][i].balance;
```
This is however done in the wrong order. Since the balance is set to 0 first the spent will not increase. This then impacts the calculation at the end where the delta is accounted for:
```solidity
stakedNFTs[_address][stakedNFTs[_address].length - 1].balance -= (amount - spent);
```
amount - spent will be too high here while the balance of the NFT was actually spent. Imagine this scenario: A user has two NFTs, with 20_000 and 10_000 XP. They spend 22_000 XP. amountPerNFT will then be 11_000. After the first iteration of the first NFT, its balance will be 9_000 and spent will be 11_000. The second iteration will go into the else clause. The balance will be set to zero (effectively spending 10_000 XP), spent will be increased by 0. Then at the last calculation amount was 22_000, spent is 11_000. This means that it will try to remove amount - spent = 11_000 more, even though what is actually spent is 11_000 + 10_000 = 21_000.

## Recommendation
Consider removing the balance before setting it to 0 in spendXP. Also consider redesigning the design used here. Another possible way is removing a proportional amount from each NFT ((amount * nft balance)/total rewards, Then iterating over the NFTs again from the top removing the delta (amount - spent) from the first possible one. In addXP use the recommendation in C-03. Simply add payPerNFT to each NFT.
