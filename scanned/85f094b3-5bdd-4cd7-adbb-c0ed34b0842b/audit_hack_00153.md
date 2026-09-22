# [H] Lodestar Finance exploit: Lodestar Finance , a Compound fork on Arbitrum, is the latest victim of the mass market manipulation that has affected both people and protocols acros

## Summary
Severity: High
Target: Lodestar Finance
Loss: $6,500,000
Published: 12/10/2022
Source: https://rekt.news/lodestar-rekt
Type: rekt-postmortem

## Details
## Lodestar Finance - REKT

 Monday, December 12, 2022 Lodestar Finance - REKT 

 read this article also in : zh 

 Lodestar Finance , a Compound fork on Arbitrum, is the latest victim of the mass market manipulation that has affected both people and protocols across our industry. 

 On Saturday, the price oracle of plvGLP collateral was manipulated, allowing the attacker to drain their lending pools for a profit of ~$6.5M.

 According to the official announcement , “ 2.8 Million of the GLP is recoverable, which is worth about $2.4 million. ” The team has appealed to the hacker to negotiate a white-hat bounty.

 The incident saw the token LODE dump by ~70% and TVL drop to just $11. 

 That’s #77 on the leaderboard for Lodestar Finance. 

 Among Lodestar’s collateral assets is the yield-bearing plvGLP, representing GLP locked in Plutus DAO ’s vault. Using flash loans, the attacker manipulated the plvGLP price reported by Lodestar’s GLPOracle contract, allowing them to “borrow” all the funds supplied on the platform.

 The Lodestar docs state that:

 we are relying on Chainlink Oracles for accurate pricing (with the exception of plvGLP) 

 An inviting note for any would-be attackers… 

 Solidity Finance summarised the root cause: 

 The GLPOracle did not properly take into account the impact of a user calling donate() on the GlpDepositor contract, which inflates the assets of the GlpDepositor contract, and therefore the oracle-delivered price of the plvGLP token.

 Lodestar’s preliminary post mortem gives further details of the exploit, as well as pointing out that “ the oracle can’t be allowed to undergo instantaneous change within the same block. ”

 Certik’s report contains a full step-by-step of the attack flow.

 Attacker’s address 0xc29d94386ff784006ff8461c170d1953cc9e2b5c 

 Example exploit tx: 0xc523c630… 

 The 343 ETH ($430k) necessary for the attack was bridged from Polygon three months ago. Following the exploit, the funds were swapped to ETH, bridged back to mainnet and dispersed to multiple addresses .

 Manipulating the price of collateral has been a popular attack technique since the beginning of DeFi, but especially in recent times, as this incident follows the attacks on both Mango and Moola Markets, who lost $115M, and $8.4M respectively, in October. 

 The above examples had funds partially or fully returned, ensuring users didn’t totally lose out. Yet two days have now passed since the initial attack on Lodestar, and no mention of any planned reparations has yet been made.

 Forking an existing project, even long-standing and resilient protocols, does not guarantee the same security. 

 But this paragraph in the Lodestar documentation suggests they may not have realised as such…

 Lodestar is a Compound fork at the core, and Compound has some of the most battle-tested contracts in all of DeFi. We have added code to support a few changes we have made, namely adding Arbitrum support, DPX, MAGIC and plvGLP support, tweaking some Interest Models, and a few other small changes.

 Time is the best security audit of all, but smart contract changes render even the most time-tested protocols open to new vulnerabilities. 

 Another market manipulated, more millions misplaced, and the market manipulators move on… 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
