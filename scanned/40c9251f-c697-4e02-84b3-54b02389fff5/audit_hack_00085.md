# [H] Deus DAO - R3KT exploit: Token holders lost a total of ~$6.5M on Arbitrum, BSC and Etherum, and the DEI stablecoin depegged over 80%

## Summary
Severity: High
Target: Deus DAO - R3KT
Loss: $6,500,000
Published: 05/05/2023
Source: https://rekt.news/deus-dao-r3kt
Type: rekt-postmortem

## Details
## Deus DAO - R3KT

 Saturday, May 6, 2023 Deus DAO - R3KT 

 read this article also in : zh 

 It’s a hat trick for Deus DAO . 

 Token holders lost a total of ~$6.5M on Arbitrum, BSC and Etherum, and the DEI stablecoin depegged over 80%. 

 This incident, just over a year since their last appearance , makes Deus DAO the third protocol with three entries on our leaderboard .

 Deus’ two previous entries were on the project’s original home, FTM, where they don’t appear to have been affected. Since then, DEI has branched out onto other chains.

 After the alarm was raised , and the root cause identified , Deus eventually acknowledged the hack, as well as confirming a multisig address for whitehats to return funds.

 But how many times can a thrice-hacked protocol be trusted? 

 Credit: _ adamb , Zellic , 0xProtosec 

 A simple implementation error was introduced into the DEI token contract, in an upgrade last month. The burnFrom function was misconfigured, with the ‘_allowances’ parameters ‘msgSender’ and ‘account’ written into the contract in the wrong order.

 This created a public (or pubic, according to Peckshield ) burn vulnerability, which an attacker is then able to manipulate and gain control of DEI holders’ approvals and transfer assets directly to their own address.

 The mis-ordered parameters allow the attacker to set a large token approval for any DEI holder’s address. Then, by burning 0 tokens from the address, the approval is updated to the attacker’s address, who can drain the holder’s funds.

 See the following step-by-step:

 identify an address with a huge amount of DEI

 approve to this address

 call burnFrom with amount = 0 and this address

 During the burnFrom it grants approves all tokens from the address to your own

 call transferFrom

 Attacker’s address (Arbitrum): 0x189cf534de3097c08b6beaf6eb2b9179dab122d1 

 Example attack tx (Arbitrum): 0xb1141785… 

 Frontrunner address (BSC): 0x5a647e376d3835b8f941c143af3eb3ddf286c474 

 Example attack tx (BSC): 0xde2c8718… 

 Attacker’s address (Ethereum): 0x189cf534de3097c08b6beaf6eb2b9179dab122d1 

 Example attack tx (Ethereum): 0x6129dd42… 

 According to BlockSec’s MetaSleuth , the losses were approximately $5M on Arbitrum, $1.3M on BSC and $135k on Ethereum. 

 Luckily, the exploit on BSC was frontrun, and an on-chain message to the Deus Deployer shows the intent to return the funds. Other whitehats also sprang into action, and over $600k in USDC has so far been returned to a recovery multisig .

 However, there were also doubts about the usefulness of giving funds back to a team that produced such a trivial bug. 

 Returning rescued funds to a thrice-hacked protocol seems rather counterproductive… 

 An official update mentions a recovery plan for users who lost out in the exploit, and Deus have reached out to the attacker on-chain.

 But given the account was originally funded via Tornado Cash on BSC, it’s not looking good.

 Will this be finally be a killing blow for Deus DAO? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
