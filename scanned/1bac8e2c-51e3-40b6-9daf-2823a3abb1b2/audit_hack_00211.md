# [H] Raft exploit: On Friday, Raft fell victim to an on-chain pirate raid, causing the project’s R stablecoin to depeg

## Summary
Severity: High
Target: Raft
Loss: $3,300,000
Published: 11/10/2023
Source: https://rekt.news/raft-rekt
Type: rekt-postmortem

## Details
## Raft - REKT

 Sunday, November 12, 2023 Raft - REKT 

 read this article also in : 

 On Friday, Raft fell victim to an on-chain pirate raid, causing the project’s R stablecoin to depeg. 

 Although the infinite mint exploit should have netted a tidy $3.3M profit, the clumsy crypto corsair dropped the loot overboard.

 1570 ETH sent to the burn address and around $8k out of pocket overall . 

 An embarrassing, but ultra-sound, self-rekt. 

 Ancilia raised the alarm , with the Raft team quickly acknowledging the incident. An hour after the initial response, came the following update :

 Update: Further minting of R has been paused.

 Existing users are still able to repay their positions and receive their collateral.

 The next day, the team informed users that a recovery plan is in the works ( rugging a rug-artist , perhaps? ), while reminding users who had minted R that they are still able to recover collateral.

 The team also advised against speculating on the now-partially-unbacked stablecoin, adding: 

 The current version of Raft will be sunsetted.

 Will they manage to keep themselves afloat for a v2? 

 Credit: Ancilia , Igor Igamberdiev , BlockSec 

 The hack involved inflating the value of collateral by liquidating previously opened positions from an address holding excess ETH (sourced via flash loan). 

 The over-valued collateral then allowed the attacker to mint 6.7M R stablecoin, which were dumped for ( what should have been ) over $3M profit.

 For a full technical breakdown of the exploit, see threads by Ancilia , Igor Igamberdiev and BlockSec . See also the team's post-mortem . 

 The freshly minted R tokens were dumped into the existing liquidity pool, causing the price to tumble: 

 The token’s collateral reserves were not affected, and any users who have a CDP on Raft should be able to return R and withdraw their collateral. 

 Attacker address: 0xc1f2b71a502b551a65eee9c96318afdd5fd439fa 

 Attack tx: 0xfeedbf51… 

 Preparatory tx: 0xa1378a4d… 

 Exploited contract: 0x9ab6b21cdf116f611110b048987e58894786c244 

 The profits, however, were not collected by the attacker, and were sent to the ETH null address 0x0000 instead. Igor Igamberdiev explains :

 The problem is that the code for converting R to ETH and transferring it to the exploiter was called from another contract using delegatecall

 But delegatecall looks at the storage of the parent contract, in which the slot with the exploit address was not initialized

 Oops indeed. 

 Despite how badly this exploit went for the attacker, they certainly aren’t stupid . 

 Raft had been extensively audited by four organisations, including Trail of Bits and a Hats Finance contest. 

 As we’ve said before, even the best audits are no silver bullet ; incidents like these show the value of continued investment in a full suite of security practices.

 But when vulnerabilities are still being found in DeFi giants , it reminds us that nowhere is truly safe. 

 When braving DeFi's stormy seas, we all must choose our vessel. 

 Would you trust a Raft? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
