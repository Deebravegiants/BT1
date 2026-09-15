# [H] Anyswap exploit: An exploit was detected in the new anyswap v3 prototype, all bridge funds used in v1/v2 are safe

## Summary
Severity: High
Target: Anyswap
Loss: $7,900,000
Published: 07/10/2021
Source: https://rekt.news/anyswap-rekt
Type: rekt-postmortem

## Details
## Anyswap - REKT

 Tuesday, July 13, 2021 Anyswap - REKT 

 read this article also in : zh 

 The bridges are burning. 
 AnySwap and Chainswap in a 24 hour period.

 Anyswap were quick to announce the incident. 

 An exploit was detected in the new anyswap v3 prototype, all bridge funds used in v1/v2 are safe.
Remedial action already in place for all exploited funds.

 Attacker’s address: 0x0aE1554860E51844B61AE20823eF1268C3949f7C 

 The funds lost were all $ pegged stablecoins totalling approximately $7.9M. 

 Just over 5.5M $MIM were taken in this transaction.

 A further 3 transactions saw a total of ~2.4M USDC stolen. 

 1: via Ethereum - 1,536,821.7694 USDC

 2: via BSC - 749,033.37 USDC

 3: via Fantom - 112,640.877101 USDC

 The root of the exploit lay in the prototype V3 Router’s use of ECDSA , the algorithm securing its MPC wallet by generating private keys.

 The key here is that every k value calculated in the algorithm should be based on a different, random number for each signature. If two or more transactions contain a repeated k value, then the private key can be back-calculated.

 This potential security flaw has been known since 2010, when console hacking group fail0verflow detailed the process here (p123-129). And its application to blockchain keys was later detailed in 2013 .

 Credit: Tayvano 

 Despite this, Anyswap’s post-mortem states that the attacker detected a repeated k value in two of the V3 Router’s transactions on BSC, and was able to back-calculate the private key.

 Anyswap stressed that “only the new V3 cross-chain liquidity pools have been affected” and that the bridge remains operational via V1 and V2 Routers. The post-mortem also states that the V3’s code has been fixed and will reopen after the 48hr timelock installed by the team expires.

 The team has also reached out to potential bug bounty hunters: 

 Anyswap will reward anyone who reports bugs to us. This will help us build truly secure and even better cross-chain solutions.

 The need for fully secure bridges grows stronger by the day, as crypto capital spreads across multiple chains. 

 However, the security architecture for cross-chain bridges is complex - proposing a puzzle to developers which has yet to be solved.

 Anyswap V3 was a prototype, so perfection was not expected, but considering the nature of the exploit, it seems this loss was preventable. 

 Although action was taken relatively quickly to prevent another attack, @nicksdjohnson is of the opinion that the patch does not do enough. 

 Setting aside the fact that there's a much better, industry standard solution to this, their patch:
Fails catastrophically (exposing users to another hack) if you accidentally delete a file, or restore from an old backup, or move to a new server.

 And it requires every signature request to scan every previous one, but really that's the smallest problem here.

 Anyswap call themselves a “trustless protocol”, but perhaps that label no longer has the desired effect after such a damning evaluation from a leading Ethereum developer.

 Do you trust the Anyswap patch? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
