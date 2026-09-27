# [M] Sturdy Finance exploit: Sturdy Finance has lost ~$800k to a price manipulation exploit

## Summary
Severity: Medium
Target: Sturdy Finance
Loss: $800,000
Published: 06/12/2023
Source: https://rekt.news/sturdy-rekt
Type: rekt-postmortem

## Details
## Sturdy Finance - REKT

 Monday, June 12, 2023 Sturdy Finance - REKT 

 read this article also in : 

 Not so Sturdy, after all. 

 Sturdy Finance has lost ~$800k to a price manipulation exploit. 

 The Ethereum-based lending protocol offers leverage for yield farmers who deposit staked assets as collateral.

 Shortly after the alarm was raised , the Sturdy Finance team acknowledged the attack:

 We are aware of the reported exploit of the Sturdy protocol. All markets have been paused; no additional funds are at risk and no user actions are required at this time.

 As noted by Ancilia , the attack vector is similar to exploits on Midas Capital and dForce Network . 

 Is this issue really still causing problems? 

 Credit: Ancilia , BlockSec 

 The attack used a flash loan to target the (unfortunately named) SturdyOracle and return a manipulated price of collateral token (B-stETH-STABLE). 

 BlockSec provided the following step-by-step:

 Attacker’s Address: 0x1e8419e724d51e87f78e222d935fbbdeb631a08b 

 Attack contract (with front-running protection built in): 0x0b09c86260c12294e3b967f0d523b4b2bcdfbeab 

 Attack Tx: 0xeb87ebc0… 

 The 442 ETH ($800k) profit was immediately deposited into Tornado Cash, completing the laundering just 20 minutes after being funded from the same source. 

 This read-only reentrancy vulnerability has been seen in a number of attacks over the last year. 

 A February post on Balancer forums noted how some Balancer pools are also susceptible to the attack vector, with the specific pools targeted in today’s attack listed as vulnerable.

 With three audits (from Certik , Quantstamp and Code4rena ), and a well-known exploit type, it is surprising that these pools were left open to attack.

 EDIT 02/06/2024: As pointed out by Quantstamp 
, the vulnerable version of the LendingPool contract did not fall within the audit scope. The leaderboard has been updated accordingly. 

 No wonder many are discussing the need for oracle-free lending systems, which is becoming a hot topic . Though, certain solutions may eventually need oracles of their own …

 Let’s hope that, in the future, we’ll be building on Sturdy-er foundations. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
