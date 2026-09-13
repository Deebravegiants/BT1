# [H] Akropolis exploit: The Akropolis has not been this rekt since the battle of Salamina in 480 B.C

## Summary
Severity: High
Target: Akropolis
Loss: $2,000,000
Published: 11/12/2020
Source: https://rekt.news/akropolis-rekt
Type: rekt-postmortem

## Details
## Akropolis - REKT

 Thursday, November 12, 2020 akropolis - delphi - REKT 

 read this article also in : zh 

Pericles must be turning in his grave. 
 The Akropolis has not been this rekt since the battle of Salamina in 480 B.C.

 A modern day King Xerses has razed the Akropolis once more, stealing $2,000,000 DAI via a combination of flash loans and re-entrancy.

 At first, the Akropolis admins tried to claim they were simply carrying out some “fixes”.
 
We now know they were burned for $2 million.
 
But how? 
 The Akropolis protocol allows users to deposit tokens into a vault and get different tokens in return. The amount of new tokens you get back depends on how much is deposited.

 The deposit amount is calculated by the difference in balance from before and after the transfer operation.

 Here’s how the attacker took advantage of this system by creating a malicious token contract which called deposit again (reentrancy). This is the attack contract.

- 
 Create faketoken

- 
 Deposit faketoken

 3a. Get a callback to faketoken, deposit 25k DAI

 3b. Get credited for 25k DAI of deposits

- 
 Get credited for 25k DAI of deposits

- 
 Withdraw 50k DAI

 Credit samczsun 
 
Because the attacker was able to use their contract as the deposit token, they were able to use reentrance with a dYdx flash loan, as shown below.
 
 This is the hackers address. We can see they had started to execute batches of $50k attacks around 8 hours prior. 
 They then sent $2m of these gains to a different address, where it remains at the time of writing.

 Credit @dogetoshi 
 
We should note that the smart contracts that the hacker interacted with had been audited by two separate security companies, Smartdec and Certik. 
 Smartdec have a reasonably good track record , however, for Certik, Akropolis is an unwelcome addition to the growing list of projects that they have audited before an exploit.

 bZx, Lien, Harvest , and now Akropolis. A completed security audit should never be taken as a guarantee of safety, but a Certik audit certainly carries less weight than it used to...

 Even a well made and thoroughly audited contract can turn into a shit show if in the hands of bad players. The fact that Akropolis were so quick to lie to their users shows that not all the blame lies on Certik or the hacker.

 Although we so often strive for trustless protocols, when it comes to human communication between a user and a service provider, the fragility of trust should always be protected.

 Akropolis have lost that trust, and become rekt.

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
