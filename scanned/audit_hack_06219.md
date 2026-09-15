# [M] Vault is vulnerable to a first depositor attack

## Summary
Severity: Medium
Reporter: kiki_dev
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L293
Type: audit-issue

## Details
# Vault is vulnerable to a first depositor attack

## Summary
When a depoist gets sent to the vault the users gets shares assigned to them. Then when they want to they withdraw an amount paportional to their shares. So if a user had 1 share and there was 1 share in total. A user could withdraw 100% of the funds. 


Fair Funding calls `deposit_underlying`  here
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L293

Which does this 
https://github.com/alchemix-finance/v2-foundry/blob/master/src/AlchemistV2.sol#L591

Fair funding uses alchemist to handle calculating shares and alchemist does as shown in the link below
https://github.com/alchemix-finance/v2-foundry/blob/master/src/AlchemistV2.sol#L1641

If at any point `_calculateUnrealizedActiveBalance()` is less than amount amount * totalShares. The return value will be 0. 

If this were to happen the Auction would be broken. Becasue of the check here The function will always revert. 
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L228

If it reverts that user will never be able to settle and the auction wil not be able to continue on to the next NFT.
## Vulnerability Detail

Here is an example:

Alice wins an auction for paying only one Wei
Alice recieves 1 share 
Alice grows the value of `_calculateUnrealizedActiveBalance` by 10eth without increase her shares (via transfer / other function calls from Alechist) 
Now alices 1 share is worth 10 WETH. 
Bob wins the next auction for 9 WETH.
When bobs shares are calculated it looks as follows:
amount x (total Shares) / _calculateUnrealizedActiveBalance()
9WETH x 1 / 10WETH = 0

The function reverts 
Alice as the sole NFT holder get all the benifits. But more importantly the protocol that started the funding does not get funding it needs.


 
## Impact
Auction will break making it impossbile to complete auction. 
The next depositor (bob) will also have there funds locked in the auction house contract. Since he cannot settle due to shares = 0. and no one else can make a bid since epoch is over. His funds will be locked in the contract permantly. 

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L293

## Tool used

Manual ReviewBob

## Recommendation
Make a initial deposit for a small amount of wei and burn. This way there is no option for a first depositor attack. if the total shares is bigger than one then the attack will end up costing too much. Or require floor to be greater than some number thats not 0.
