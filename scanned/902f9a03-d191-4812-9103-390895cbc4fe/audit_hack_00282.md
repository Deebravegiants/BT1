# [C] Uwulend exploit: UwuLend, a lending protocol launched by Frog Nation's former CFO Sifu , was hacked for $19.4 million due to an oracle manipulation attack

## Summary
Severity: Critical
Target: Uwulend
Loss: $19,400,000
Published: 06/10/2024
Source: https://rekt.news/uwulend-rekt
Type: rekt-postmortem

## Details
## Uwulend - Rekt

 Monday, June 10, 2024 Uwulend - REKT 

 read this article also in : zh 

 UwuLend, a lending protocol launched by Frog Nation's former CFO Sifu , was hacked for $19.4 million due to an oracle manipulation attack. 

 The attack, first identified by Cyvers , utilized a series of three transactions within six minutes to convert stolen $WBTC and $DAI into $ETH after being funded from Tornado Cash. 

 UwuLend acknowledged the exploit roughly an hour later, pausing the protocol while the team investigated the situation.

 The $19.4 million in drained capital was swiftly moved across two Ethereum addresses in a blitz strike choreographed with criminal precision. 

 For a protocol that had recently passed a robust security audit, this blindsiding exploit represented a nightmarish rug pull from the UwuLend depositors' perspective.

 In light of the exploit, skeptics can't help but raise an eyebrow at Sifu's involvement. 

 With his history of controversies, the question on everyone's mind is, has the former Frog Nation CFO orchestrated yet another masterful deception in the crypto realm? 

 Credit: Cyvers Alerts , UwuLend , Nick Franklin , CRV Hub 
 Uwulend’s contract is a fork version of AAVE V2, but they changed the oracle fallback logic to borrow assets at one rate and liquidate them at an artificially inflated rate as seen here . 

 According to root cause analysis by Nick Franklin , the exploit took advantage of a price discrepancy in UwuLend's oracles.

 To manipulate the price, the attacker utilized a flash loan. UwuLend's fallback oracle calculated prices based on the state of several Curve pools.

 The attacker could manipulate the pool states by making large trades with the borrowed tokens. 

 This manipulated the price feed, allowing the attacker to borrow sUSDe at 0.99 but liquidate positions at the inflated 1.03 rate. 

 Attacker: 
 0x841ddf093f5188989fa1524e7b893de64b421f47 

 Attack transactions: 

 0x242a0fb4fde9de0dc2fd42e8db743cbc197ffa2bf6a036ba0bba303df296408b 

 0xb3f067618ce54bc26a960b660cfc28f9ea0315e2e9a1a855ede1508eb4017376 

 0xca1bbf3b320662c89232006f1ec6624b56242850f07e0f1dadbe4f69ba0d6ac3 

 The stolen funds are parked in the following two addresses: 

 0x48d7c1dd4214b41eda3301bca434348f8d1c5eb6 

 0x050c7e9c62bf991841827f37745ddadb563feb70 

 One person was hit harder than most, Michael Egorov the founder of Curve was robbed of just over 23.5 million CRV ($9.85M) that he deposited into UwuLend. 

 The attacker deposited the tokens into Curve’s Llama Lend and borrowed just over 8 million crvUSD ($8.11M).

 Thanks to the diligent lenders of crvUSD in LlamaLend's CRV market, the hacker's position was fully hard-liquidated as the lenders repaid the debt, being one of the little silver lining of this event by proving the robustness of the platform. 

 The situation and effects are being unpacked and analyzed in real time in the Curve Social Telegram channel.

 Sifu extended an on-chain olive branch to the attacker, proposing a 20% white hat bounty if they cooperate by June 12, 17:00 UTC. 

 Post-deadline, the bounty will shift gears, rewarding anyone who can expose and help bring the exploiter to justice.

 Someone else sent an onchain message to the hacker with instructions on how to move the funds without getting caught. 

 The same address has sent messages in the past to the exploiter of Gala Games , PlayDapp and Exactly Protocol to name a few. 

 UwuLend was audited by Peckshield , who characterized the code as “well designed and engineered,” with “no high-severity or critical issues” detected.

 How did such a critical oracle vulnerability go uncaught by the auditors? 

 The $19.4 million UwuLend exploit leaves more questions than answers. 

 Despite a recent security audit, a seemingly elementary oracle vulnerability paved the way for one of 2024's most bizarre thefts. 

 With the attacker's identity still shrouded in mystery, suspicion has fallen on Sifu, who appears to be a common thread in multiple crypto crime scenes.

 Questions linger about UwuLend's choice to rely on DEX prices as a fallback oracle. 

 As conspiracy theories swirl, it remains unclear if the UwuLend attack was an unfortunate lapse in security or something more nefarious.

 The overlapping breadcrumb trail of Sifu's involvement, the unorthodox oracle design, and the enigmatic on-chain instruction adds further intrigue. 

 Who is the shadowy figure instructing exploiters and are there other cryptic connections that have yet to be uncovered or is it just somebody trying to exploit the attacker? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
