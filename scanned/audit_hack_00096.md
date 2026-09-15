# [C] Elephant Money exploit: An audit couldn’t protect Elephant Money from the on-chain poachers

## Summary
Severity: Critical
Target: Elephant Money
Loss: $22,200,000
Published: 04/12/2021
Source: https://rekt.news/elephant-money-rekt
Type: rekt-postmortem

## Details
## Elephant Money - REKT

 Wednesday, April 13, 2022 Elephant Money - REKT 

 read this article also in : zh 

 An audit couldn’t protect Elephant Money from the on-chain poachers. 

 Solidity Finance failed to notify Elephant about a price manipulation vulnerability, which was then exploited in a flash loan attack that this Elephant will want to forget.

 The official post-mortem stated a loss of $11.2M, yet Peckshield later pointed out that Elephant had chosen not to include the loss of ~30 billion ELEPHANT tokens, bringing the total amount lost to $22.2M.

 “DO NOT SELL” say Elephant Money .

 Is this… financial advice? 

 Credit: BlockSecTeam 

 The attacker used flash loans to manipulate the price of the ELEPHANT token during the minting process of the project’s stablecoin TRUNK. 

 Example tx: 0xec317deb2f3efdc1dbf7ed5d3902cdf2c33ae512151646383a8cf8cbcd3d4577 

 Firstly, the attacker took flash loans of 131k WBNB and 91M BUSD, the 131,162.00 WBNB was swapped to 34.244e21 ELEPHANT.

 TRUNK can be minted by depositing BUSD. During this process, the vulnerable contract first swaps BUSD to WBNB and then uses the WBNB to buy ELEPHANT, raising the price of ELEPHANT. By minting, the attacker both receives TRUNK and increases the value of the ELEPHANT from the previous step.

 The attacker then swapped the ELEPHANT, originally acquired for 131k WBNB, to 164k WBNB. Additionally, the attacker redeemed the TRUNK for 37k WBNB and 67M BUSD, making for a total of ~200k WBNB and ~67M BUSD. After returning the flash loans (of 131k WBNB and 91M BUSD), this resulted in a profit of ~$4M

 The same process was repeated on a cycle, leading to total gains of over 27k WBNB ($11.2M) for the hacker. Since the incident, the funds have been sent on to various accounts and then either bridged to Ethereum or sent to Tornado Cash, as can be seen in the visualisation below .

 Position #28 on the leaderboard for Elephant Money , despite their attempt to downplay the loss. 

 The price of $ELEPHANT is now down by 75%, and their “stable”coin TRUNK fell by 40%, before partially recovering to $0.78.

 It’s a standard story of flash loans and price manipulation. 

 The most entertaining part is this headline / financial advice from the Elephant Money marketing department.

 So we buy the tops… then we sell the… ? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
