# [H] Conic Finance exploit: Conic Finance got double-rekt on Friday, losing a total of $4.2M from their ETH and crvUSD omnipools

## Summary
Severity: High
Target: Conic Finance
Loss: $4,200,000
Published: 07/21/2023
Source: https://rekt.news/conic-finance-rekt
Type: rekt-postmortem

## Details
## Conic Finance - REKT

 Tuesday, July 25, 2023 Conic Finance - REKT 

 read this article also in : 

 Lightning does strike twice. 

 Conic Finance got double-rekt on Friday, losing a total of $4.2M from their ETH and crvUSD omnipools. 

 Omnipools accept single asset deposits, which are then spread across a variety of Curve pools to earn LP rewards for depositors.

 As the news spread, Conic quickly acknowledged the first attack, which drained the ETH pool of $3.3M. Following the second incident, the team decided to shut down all pools. 

 The initial hack was yet another instance of the notorious read-only reentrancy vulnerability which has wreaked havoc on DeFi over the last year. Sturdy Finance , Midas Capital and dForce Network , amongst others, have all suffered from the issue in recent months.

 Both attacks were frontrun, with the recipient of funds from the second incident (an MEV bot ) returning 90% of their profits (81 ETH) the following day.

 With the majority of lost funds (over 1700 ETH) still sitting in the address of the first attack’s frontrunner, there is still hope for recovery … 

 …but given the address had previously been labelled by Blocksec as “LadyPepe Token Exploiter”, we probably shouldn’t hold our breath. 

 Credit: BlockSec , Conic Finance 

 The first attack exploited the common read-only reentrancy vulnerability in order to manipulate token prices, as discussed in many previous articles. 

 In this case, the attack can be summed up with the following TLDR by pcaversaccio:

 TL;DR: Due to a read-only reentrancy vulnerability in the oracle contract 
```
CurveLPOracleV2
```
, the attacker can reenter 
```
rETH-f.totalSupply()
```
 (and other tokens like steCRV) and thus can manipulate the prices accordingly. Thus, the attacker can withdraw more than deposited.

 A more detailed breakdown can be found in Daniel Von Fange’s thread .

 According to auditors Peckshield, the vulnerability was identified in the audit , however a new oracle contract reintroduced the bug. 

 FWIW, our audit identifies a similar read-only reentrancy issue. However, the same issue is introduced in the newly introduced CurveLPOracleV2 contract, which was not part of the audit scope.

 Conic dev 0xWicket later clarified that the contract did have inbuilt reentrancy protection, however it wasn’t triggered due to a mix-up between ETH and WETH addresses.

 We are currently in the process of writing a post-mortem. The root cause of this being exploitable was our assumption that ETH was treated as address 0xeee... by Curve, while it uses the the WETH address for V2 pools. Our reentrancy protection failed to trigger because of that

 Exploiter address (1st attack): 0x8d67db0b205e32a5dd96145f022fa18aae7dc8aa 

 Over 1700 ETH (around $3.3M) was forwarded to a secondary address: 0x3d32c5a2e592c7b17e16bddc87eab75f33ae3010 

 Exploit tx (1st attack): 0x8b74995d… 

 Original failed tx (1st attack): 0x97a8315e… 

 Original exploiter address (1st attack): 0x10db234e02c3889d8e408c7084e8ce10892bdad7 

 The second attack was somewhat simpler and far less damaging , apart from to Conic’s reputation. The issue was described in Conic’s post-mortem as a type of sandwich attack on imbalanced pools. 

 The attack steps are as follows:

 Exchange crvUSD to USDC in the Curve pool

 Deposit crvUSD into Conic

 Exchange USDC to crvUSD in the Curve pool

 Withdraw from Conic

 Repeat steps above

 The report goes on to explain that:

 The attacker would benefit from the exchanges in the Curve pool by exchanging at a favorable rate. While we did have some mechanism in place to ensure we did not interact with imbalanced Curve pools, the bounds that we had set were not tight enough and allowed the attacker to slowly drain funds from the pool.

 A total of approx. $934,000 was stolen from the crvUSD Omnipool, giving the attacker a profit of approx. $300,000.

 Exploiter address: 0xb6369f59fc24117b16742c9dfe064894d03b3b80 

 Example hack tx: 0x37acd17a… 

 Frontrunning bot (returned 81 ETH): 0xd050e0a4838d74769228b49dff97241b4ef3805d 

 For all the talk of the Curve Wars , the wider ecosystem feels Conic's pain.

 The Curve team got involved in warning users of the dangers, and even suggesting safe havens for farmers.

 Conic’s was one of the most hotly anticipated DeFi projects before launching earlier this year, and was seen by some threadoors as a contender for being the next cycle’s CVX/Yearn.

 Pre-hack, CNC was sitting at around $6. News of the initial incident caused a drop in price of around 35% with a further fall to just $1.72 following the second exploit. CNC has since settled at around $2.75, just below half of its pre-hack value.

 The TVL chart shows just how much damage Friday’s events have done, with less than a third of Conic’s pre-hack TVL remaining: 

 Will such a promising protocol survive this double-blow? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
