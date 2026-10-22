# [C] Deus DAO exploit: On 15th March, the project’s users were liquidated for a total of $3M

## Summary
Severity: Critical
Target: Deus DAO
Loss: $13,400,000
Published: 04/28/2022
Source: https://rekt.news/deus-dao-rekt-2
Type: rekt-postmortem

## Details
## Deus DAO - REKT 2

 Thursday, April 28, 2022 Deus DAO - Fantom - REKT 

 read this article also in : zh 

 Deus DAO dealt double damage. 

 On 15th March, the project’s users were liquidated for a total of $3M.

 In an unfortunate sequel, the protocol has now lost a further $13.4M.

 Deus DAO recognised the exploit stating that:

- 
 User funds are safe. No users were liquidated

- 
 DEI lending has been temporarily halted

- 
 $DEI peg has been restored.

 This attack used a similar technique to the first; oracle manipulation to inflate the value of DEI collateral, however this time the process was more complex.

 In last month’s article we asked: 

 Why didn’t Deus DAO have a more robust system in place? 

 In Deus DAO’s official response , Lafayette Tabor explained that the integration of Muon’s off-chain VWAP oracle was “ designed exactly to prevent this ”.

 It was then announced on Discord on March 19th that “Muon oracles are ready and implemented”.

 But it seems the new system wasn't enough to keep the protocol safe. 

 How did the attacker bypass the new oracle?

 This exploit was not as straightforward as the last. 

 The hacker needed to trick the off-chain (Muon) oracle as well as manipulate the on-chain price feed (the same USDC/DEI pool as before) .

 The Muon oracle monitors transactions within the Solidly USDC/DEI pool to calculate a Volume Weighted Average Price (VWAP). Four minutes before the main attack transaction, a separate transaction was able to “fake” a swap of ~2M USDC to 100k DEI.

 The funds necessary to finance this manipulation were initially withdrawn from Tornado Cash before being sent on to the exploiter’s address, swapped for $2M USDC and then sent via Multichain to Fantom (example tx: send , receive ).

 In what Tabor claims to be a “ a zero-day exploit on Solidly swaps ” , a series of flash-swaps inside the same pool outputs a manipulated price, which is read by the Muon oracle.

 He went on to explain via DM that:

 ”we came to the conclusion it all is based on the fact the muon oracle implementation only used Solidly as a price source, they have been working on upgrading that already.

 the swap used flashswap() that wasnt filtered out properly by muon leading to a short term VWAP price glitch…

 …Main takeaway based on the whitehackers anlysis is to change muon vwap pricing to filter out obscure swaps and use multiple data sources."

 After having prepared the Muon oracle, at 02:40 UTC, the main attack targeted the USDC/DEI pool used by the lending contract as an on-chain oracle for DEI, using the same process as before.

 Credit: Peckshield 

 1: Flashloan 143,200,000 USDC

 2: Swap 143,200,000 USDC to 9,547,716 DEI via sAMM-USDC/DEI_USDC_DEI (so DEI becomes extremely expensive)

 3: With 71,436 DEI as collateral, attacker borrows 17,246,885 DEI from DeiLenderSolidex due to the manipulated price in step 2

 4: Repay flashloan with ~$13M as hack profit

 While last month’s attack manipulated collateral price in order to liquidate borrowers, this time, the collateral was used to borrow funds directly from the protocol. 

 The loot (5446 ETH, including the funds used to finance the Muon manipulation) was sent from the attacker’s address on Fantom to Ethereum and then on to Tornado Cash.

 Muon oracle manipulation tx: 0x8589e1… 

 Main flashloan attack tx: 0x39825f… 

 Attacker’s address (FTM): 0x701428… 

 Attacker’s address (ETH): 0x701428… 

 Despite this being the second incident to affect the project in as many months, the price of DEUS has returned close to pre-hack prices, after an initial ~20% drop. DEI has been trading under peg since the incident, but appears to be stabilising over time.

 Given the oracle is a new product and the swap vulnerability is allegedly previously unknown, it's no surprise that the Armors Labs’ audit of Deus’ lending product did not pick up the issue. 

 However, even if the claims of a novel vulnerability are accurate, Tabor’s admissions show that the Muon oracle wasn’t up to task - it shouldn’t have been using a single price source, and had inadequate filtering of “obscure swaps”.

 Both of these factors will be addressed and, similarly to last time, the project will be covering losses , this time via veDEUS funds.

 There are reliable, established and already battle-tested options to choose from.

 While innovation is admirable, security standards emerged from our baptism of fire. 

 Let’s make sure to use them. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
