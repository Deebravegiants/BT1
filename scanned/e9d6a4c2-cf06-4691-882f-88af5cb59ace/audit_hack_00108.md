# [H] Gamma Strategies exploit: Bold strategy, Gamma, let’s see if it pays off…

## Summary
Severity: High
Target: Gamma Strategies
Loss: $4,500,000
Published: 01/04/2024
Source: https://rekt.news/gamma-strategies-rekt
Type: rekt-postmortem

## Details
## Gamma Strategies - REKT

 Thursday, January 4, 2024 Gamma Strategies - Arbitrum - REKT 

 read this article also in : 

 Bold strategy, Gamma, let’s see if it pays off… 

 Gamma Strategies, an Arbitrum-based concentrated liquidity management protocol, was exploited for at least $4.5M, earlier today. 

 Security researchers initially thought CryptoAlgebra was the affected protocol, before the victim was later correctly identified as Gamma.

 The attack began around 03:30 UTC, with the alarm quickly raised and Gamma acknowledging the hack approximately an hour and a half after it commenced. 

 A follow-up announcement informed users that the team had paused deposits to mitigate further attacks:

 All public vaults/hypervisors have had deposits shut down. You may withdraw your funds if need be. Our vaults will continue to be managed normally for now, but deposits are currently shut down until we identify and mitigate the problem.

 When Orbit lost over $80M at New Year, we asked: 

 Can we do better this year?

 So far, it’s not looking good … 

 Credit: Gamma Strategies , CharlesWang , PeckShield 

 Gamma published a thread outlining the preliminary cause of the exploit. However, a full post-mortem is forthcoming. Paladin’s CharlesWang outlined a potentially similar attack vector. 

 Flash loans were used to manipulate the value of deposits, allowing the attacker to mint an inflated number of LP tokens. 

 Despite four desposit protection measures, the attack was viable due to the broad ranges in allowed price changes within certain vaults. Deposits remain paused on Gamma vaults, as it is during deposits that the attack vector arises.

 As Gamma explained :

 The main issue is with the settings we placed on (2) the price change threshold.

 It was placed too high allowing for up 50-200% price change on certain LST and stablecoin vaults. This allowed the attacker to manipulate the price up to the price change threshold and mint a disproportionately high number of LP tokens.

 Peckshield provided an attack flow:

 Attacker address ( ETH , ARB ): 0x5351536145610aa448a8bf85ba97c71caf31909c 

 Attack contract 1: 0x4b57adc00ac38f74506d29fc4080e3dc65b78a69 

 Example attack tx: 0x025cf285… 

 The majority of funds were bridged back to the hacker’s Ethereum address . USDT was then swapped out for ETH for a total of 1535 ETH ($3.4M). Approximately $1.1M of DAI and gDAI remains on Arbitrum , however total losses to Gamma may have been higher .

 The attacker was funded via Tornado Cash two and a half hours before the attack began. 

 The team has contacted the attacker on-chain, seemingly hoping for a whitehat. But the 1000 ETH deposited into Tornado Cash doesn’t paint an optimistic picture.

 Collateral damage threatened a number of other projects… 

 First, Crypto Algebra suffered reputation-wise from the initial mis-labeling, then other protocols paused their contracts out of an abundance of caution. DEXs Camelot and Quickswap were also keen to point out that the issue was not with their own code.

 However, BlockSec did note a series of smaller scale attacks on similar protocol Dyson Money . 

 Gamma Strategies has a somewhat chequered past. 

 Before rebranding, the protocol then known as Visor Finance suffered three incidents in 2021 alone. 

 In June they defended the loss of $500k via a privileged function as “ not a rug ”, then in November they downplayed another hack as “ economic arbitrage ”.

 December 2021’s loss of $8.2M to an infinite mint bug seems to have been the nail in Visor’s coffin, with the rebrand and token migration announced two days later.

 However, it bears mentioning that Gamma has had no issues since the rebrand, with apparently “ no original developers or founders remaining from the project ”. 

 The protocol has undergone three audits , from Consensys Diligence ( March 2022 ), Arbitrary Execution ( March 2022 ), and Certik ( July 2021 ), but given that the vulnerability was due to the configuration of individual pool’s price change tolerances, the bug is likely out of scope.

 As we press on into 2024, it seems the constant stream of hacks and exploits shows no sign of slowing down. 

 And if we do see a new bull run, at this rate it will surely eclipse the madness of last time.

 Stay safe out there… 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
