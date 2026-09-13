# [M] Orange Finance exploit: Orange Finance squeezed out $843.5k to kick off 2025

## Summary
Severity: Medium
Target: Orange Finance
Loss: $843,500
Published: 1/7/2024
Source: https://rekt.news/orange-finance-rekt
Type: rekt-postmortem

## Details
## Orange Finance - Rekt

 Thursday, January 9, 2025 Orange Finance - Rekt - Private Key Leak 

 read this article also in : 

 Orange Finance squeezed out $843.5k to kick off 2025. 

 Private keys - the gift that keeps on giving to opportunistic hackers hunting for low-hanging fruit. 

 Somewhere between Tuesday night's darkness and Wednesday morning's light, Orange Finance's admin keys slipped through fingers like digital butter, leaving their Arbitrum-based protocol ripe for plucking.

 Christmas may be over, but someone still found their way into Orange's stocking, upgrading contracts and draining funds faster than a New Year's champagne toast.

 The protocol's damage control playbook unfolded predictably - another private key compromise, another protocol's funds finding a new home. 

 When will DeFi protocols learn that private keys make better presents for hackers than security solutions? 

 Credit: Orange Finance , Peckshield 
 The digital heist unfolded like clockwork on a quiet Tuesday night. 

 Orange Finance's team found themselves watching helplessly as their admin access slipped into unauthorized hands.

 The attacker, armed with a compromised private key, wasted no time exercising their newfound powers.

 A swift contract upgrade later, and Orange Finance's protocols transformed into well-oiled extraction machines.

 "The contract is no longer Orange," the team announced grimly . 

 PeckShield quickly amplified the warning , urging users to steer clear of the compromised protocols and revoke their approvals.

 But it was too late, the protocol was already squeezed to a pulp. 

 Here is how they got juiced… 

 Attacker Address: 
 0x496e5a7ba67735c7ee5eb81ef07b65b909a31345 

 Attack Contract: 
 0x17c8eA17F174B5fa49D5090933ff28cE2DF10a3c 

 The Attack Sequence as follows… 

 Initial Token Sweep: 
 0x093673927fc38783d37717b4bd14693c29035fceff6a0c7747db21e88c4ea28f 

 SYK Rewards Drain: 
 0x855625c6775b0acd5048b0c94466f76c3c361e2269445e66ae7ae352f04f538f 

 Vault Access Removal: 
 0x14535a9c8e7d5fa2c94de52067a3cf93369273517532e0a06871ddceb3e67dd7 

 Stryke Position Burns: 

 Batch 1: 
 0xad0d094c8ea32110ee3bc00d9ba040a79f5ba411296cef5e9b4d25a2c2e2a888 

 Batch 2: 
 0x1bab3323ed9d1bdea9f57809e47b93b0fc0cd154e003e96812c333dedd74c500 

 Asset Transfers (WETH-USDC): 
 0xecd160e3027b7bdd23423358f68b25eaaee08a9156f745390e14c7b7e9363195 

 Approval Exploitation: 
 0xe31cc5011c7c4ee0720674a38147f9d4765f09e138c4f1d15c45079e2b5507b3 

 Final Token Swaps: 
 0x38e5199e52eb602b48c7b63e818939908590d341e0b348c208decab146d0e556 

 Attacker move funds to another address: 

 0xeB0f537A7a1C3E38d4F57026982c11F6886233D7 

 Then makes their exit through Stargate: 

 0x02bb823d37158314680e39354d690f9182c540f6f345bacc5f4c147b60483876 

 The protocol’s juice was squeezed and bottled—here’s the final pulp tally: 

 Uniswap WETH-USDC : $135,709.63

 Uniswap USDC-ARB : $100,278.28

 Uniswap USDC-WBTC : $83,546.96

 Uniswap BOOP-WETH : $20,109.71

 Pancake WETH-USDC : $259,376.45

 Pancake USDC-ARB : $65,917.20

 Pancake USDC-WBTC : $146,541.50

 Sushi WETH-USDC : $15,519.62

 Sushi USDC-WBTC : $4,414.83

 OrangeDistributor : $12,142.71614

 Deposit losses: $783,966.93

 Losses due to approvals: $47,447.26

 Unclaimed SYK reward losses: $12,142.71614

 Total losses: $843,556.90

 With the damage done and assets flowing out, Orange Finance shifted into recovery mode. 

 Their initial response followed the familiar incident response playbook: a warning to users against protocol interaction, instructions for contract approval revocations, and finally , a negotiation attempt with their attacker. 

 "If you respond positively to our offer within 24 hours, we guarantee that no law enforcement agencies will be involved, and the matter will be treated as a white-hat hack."

 Their follow-up investigation revealed a string of operational failures - not only no monitoring framework and inadequate processes for privileged access, but most critically, their supposedly secure multi-sig wallet configured to execute with a single signature.

 Now Orange Finance promises a detailed spreadsheet documenting each user's losses, as if tabulating the damage makes it hurt less.

 Meanwhile, their investigation into how the private key leaked continues - presumably right after they figure out why leaving a door unlocked might lead to theft. 

 How many more protocols need to learn that a multi-sig wallet is only as strong as its configuration? 

 Private key compromises continue to plague DeFi with mechanical regularity, each incident following the same script - vulnerability, exploit, investigation, report. 

 Yet protocols keep treating basic security like an optional upgrade rather than the foundation it needs to be. 

 Orange Finance's follow-up investigation reads like a "what not to do" manual in protocol security.

 No monitoring framework, no proper access controls, and a multi-sig wallet with all the security of a garden fence.

 All while users watch their funds vanish faster than their faith in Web3.

 The team promises spreadsheets tracking losses and investigations into leaked keys, but these administrative band-aids can't stop the bleeding of bad security practices. 

 When your contract is "no longer Orange," how long until your whole protocol starts to rot? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
