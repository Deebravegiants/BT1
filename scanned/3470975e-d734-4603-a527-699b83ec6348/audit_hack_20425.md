# [M] OtterSec: The story of the curious rent thief

## Summary
Severity: Medium
Published: Fri, 19 Aug 2022
Source: https://osec.io/blog/solend-rent-thief/
Type: security-research

## Details
## The story of the curious rent thief

 OtterSec Aug 19, 2022 #solana #report A tale of pickpockets preying on the Solana ecosystem. Read our investigation into the persistent theft of rent from uninitialized accounts. This is the story of the Solend rent thief.

## Introduction 

 Recently, thereâs been a rent thief. This bot steals money from uninitialized accounts across the Solana ecosystem, claiming and profiting from the rent. The Solend team noticed the bot when it attempted an attack on the new permissionless pools that are being developed. Letâs dig into how rent thieving works by doing a case study on an attack on one of the permissionless pools.

 Note To be clear, funds stored in the main Solend protocol are completely unaffected.

## Background 

 To understand how this exploit works, we first have to understand a bit about how rent works in Solana.

 Since accounts can store data that every validator needs to download, Solana charges a certain amount of rent based on the amount of data. However, accounts that have enough for two years of rent payments are considered rent-exempt as long as their balance never drops below the threshold. Fortunately, rent is very cheap, so itâs not hard to make an account rent-exempt.

 As such, when creating new accounts, most programs will need to transfer some SOL into the new account to make it rent-exempt.

## The exploit 

 New reserves (also known as assets) are added to a Solend pool by calling the 
```
 init_reserve 
```
 function, which creates six new accounts to store data about the reserve:

- Reserve detail , which stores information about the reserve, e.g. liquidity mint, mint decimals, oracles, configs, etc.

- Reserve liquidity token account , which holds deposited tokens.

- Fee receiver token account , which will receive origination fees on borrows.

- Reserve collateral mint account , the deposit receipt token, also known as 
```
cTokens
```
.

- Reserve collateral token account , which holds usersâ collateral tokens.

- Creator collateral token account , the creatorâs 
```
cToken
```
 account.

 Account creation and initialization are usually done within the same transaction. However, due to Solanaâs transaction size limit of 1232 bytes, the creation and initialization of these six accounts had to be separated into two transactions: creation and initialization. Hereâs what a call to 
```
 init_reserve 
```
 is supposed to look like:

 Notice anything amiss? In between the two transactions, the account has rent money but no owner. This is where the rent thief comes in to snatch the account, along with its rent:

 Since there was a roughly 40-second (50-slot) window in between the two transactions, such an attack was very consistent.

 Fortunately, rent is relatively cheap, so the entire attack only extracts about 0.0082 SOL every iteration (four token accounts each worth around 0.002 SOL), which is around 28 cents at the time of writing this article.

 Despite this low cost, this is pretty annoyingâ¦

## Example 

 Letâs take a look at a real attack .

 Transaction 1 :

 (â¦more accounts truncated)

 The developer creates a couple of accounts and transfers enough SOL for them to be rent-exempt. This took place in slot 136,580,113.

 Attackerâs transaction :

 (â¦more accounts truncated)

 As detailed before, the attacker takes ownership of the newly created accounts. This took place in slot 136,580,154, which is 41 slots (29 seconds) after the initial transaction.

 Transaction 2 :

 The developer attempts to take ownership of the account, but it fails with the error âaccount or token already in useâ since the attacker took ownership of it. This took place in slot 136,580,167, which is 13 slots (9 seconds) after the attackerâs transaction. In total, thatâs a 54-slot gap (38 seconds) between the two Solend transactions.

 Attackerâs transaction :

 (â¦more accounts truncated)

 Now that the attack is over, the attacker closes the accounts, transferring the rent money to themselves. The total money stolen during this attack was 0.00815212 SOL.

## Impact 

 Rent-thieving attacks donât steal much money.

 They can only make a small profit very infrequently as Solana rent is cheap and there are only a handful of large services that separate account creation and initialization. In addition, this strategy doesnât scale well, since such non-atomic account creation is relatively infrequent.

 However, itâs still obnoxious even if the monetary impact is minimal. Transactions will fail and need to be remade, impacting usability.

## Solution 

 As a temporary stopgap, Solend refactored their codebase to lower the 40-second delay between transactions to around 15 seconds (20 slots), making an attack much more difficult and inconsistent.

 As a more permanent solution, Solend implemented an onchain program which handles account creation, allowing them to fit all the relevant instructions into one transaction.
