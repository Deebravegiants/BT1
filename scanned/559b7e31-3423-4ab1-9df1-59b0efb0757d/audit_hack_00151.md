# [H] Levyathan exploit: Levyathan.finance sank last week, along with its TVL of $1.5M

## Summary
Severity: High
Target: Levyathan
Loss: $1,500,000
Published: 07/30/2021
Source: https://rekt.news/levyathan-rekt
Type: rekt-postmortem

## Details
## Levyathan - REKT

 Thursday, August 5, 2021 Levyathan - REKT 

 read this article also in : zh 

 Another TVL taken by a mysterious monster. 

 Levyathan.finance sank last week, along with its TVL of $1.5M.

 The team have since issued a few tone-deaf tweets and long-winded Medium posts trying to shift the blame, but we’ll tell you how we see it.

 The Levyathan developers left the private keys to a wallet with minting capability available on Github. 

 ~Four months later, these keys were used to mint and dump LEV into oblivion.

 Afterwards, when users tried to redeem what was left of their money, a bug in the withdrawal mechanism meant that their worthless tokens were also irretrievable...

 “Have a nice day”

 Said the Levyathan admins. 

 The official post-mortem is almost irrelevant when you realise that they made it so easy for anyone to mint their token. 

 As a result of the exploit, users were forced to use emergencyWithdraw() to attempt to retrieve their staked tokens. 

 However, the emergencyWithdraw() logic contained a bug which referenced rewardDebt (a variable related to reward calculation) instead of user.amount as the quantity of tokens to be withdrawn.

 Some users who were quick to withdraw in this way noticed that they were receiving more tokens than expected, and continued to withdraw more and more LEV, depleting the contract and leaving nothing for those who came later. 

 In their post mortem Levyathan provided an address to which users could return funds ”in an anonymous manner", which has received 3 billion dog tokens and one PLUGANAL.

 The team later on provided a second address which has so far received ~150,000 BUSD ( coming from the first address provided by the Levyathan team ) .

 What a shitshow. 

 Leaving clearly labelled private keys visible on a public repo is unthinkable.

 Especially when they grant access to total control (no multisig) over your protocol’s native token.

 In their latest clumsy communication , the Levyathan team pointed out the fact that as the private keys were publicly available, we can be sure “that it was not an inside job”.

 Until they said that, we had assumed incompetence, but could the Levyathan team be stupid enough to to try and set up this “exposed keys” situation as an alibi?

 You decide... 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
