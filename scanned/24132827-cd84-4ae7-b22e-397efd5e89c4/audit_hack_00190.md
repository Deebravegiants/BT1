# [H] Orion Protocol exploit: Orion Protocol fell prey to a reentrancy exploit on Thursday, losing a total of $3M on ETH and BSC

## Summary
Severity: High
Target: Orion Protocol
Loss: $3,000,000
Published: 02/02/2023
Source: https://rekt.news/orion-protocol-rekt
Type: rekt-postmortem

## Details
## Orion Protocol - REKT

 Saturday, February 4, 2023 Orion Protocol - REKT 

 read this article also in : zh 

 The hunter has become the hunted. 

 Orion Protocol fell prey to a reentrancy exploit on Thursday, losing a total of $3M on ETH and BSC. 

 The project is a ‘liquidity aggregator’ aiming to bring CEX liquidity on-chain (not to be confused with Orion Finance who rugged $320k on Arbitrum the day before).

 A few hours after the news spread on Twitter, Orion’s CEO announced the loss, clarifying that the damage was contained to an internal broker account and that user funds remain safe.

 Orion’s website states:

 WHY WE EXIST

 No one has solved liquidity, custody, accessibility, and scalability in one platform.

 Until now.

 Perhaps they should have added security to that list… 

 Credit: SlowMist , Peckshield 

 The attacker used manipulated swaps of flash loaned stablecoins, artificially depositing the assets twice before withdrawing the inflated balance. 

 By creating a fake token (ATK) and routing a swap of the flash loaned funds via ATK, a reentrancy hook called depositAsset within ATK’s transfer function, effectively doubling the attacker’s account balance.

 Slowmist provided a detailed breakdown of the attack: 

 The attacker first called the depositAsset function of the ExchangeWithAtomic contract to make a deposit of 0.5 USDC tokens in preparation for the following attack:

 Next, the attacker makes a flashloan of 284,700 USDT and then calls the doSwapThroughOrionPool function of the ExchangeWithAtomic contract to swap the tokens, the exchange path is "USDC -> ATK(malicious token created by the attacker) -> USDT".

 The out amount of the exchange is the USDT balance in the ExchangeWithAtomic contract after the exchange minus the initial balance of 2,844,700 USDT.

 The problem arises when a call to the ATK token transfer function during the exchange causes the attacker to re-enter the ExchangeWithAtomic contract depositAsset function, resulting in the transfer of 284.4 million USDT from the flashloan to the ExchangeWithAtomic contract.

 The attacker's deposit in the ExchangeWithAtomic contract is recorded as 2,844,700 and the balance of USDT tokens in the contract becomes 5,689,000. As a result, the attacker's exchange of USDT is calculated as 5,689,000 minus 2,844,700.

 By calling the library function creditUserAssets to update the attacking contract's ledger in the ExchangeWithAtomic contract used the exchanged USDT, resulting in the attacking contract's final deposit of USDT in the ExchangeWithAtomic contract being recorded as 5.68 million.

 Finally, the attacker withdraws the USDT and returns it to the flashloan lender and swaps the remaining 2.836 million USDT into WETH for profit. The attackers used the same method to launch an attack on the BSC chain and made $191,000 in profit.

 The root cause of the attack was the contract exchange function is not protected from reentrancy...

 Peckshield produced the following diagram showing the basic attack steps:

 Attacker address 1 ( ETH , BSC ): 0x3dabf5e36df28f6064a7c5638d0c4e01539e35f1 

 Attacker address 2 ( ETH , BSC ): 0x837962b686fd5a407fb4e5f92e8be86a230484bd 

 Example tx (BSC): 0xfb153c57… 

 Example tx (ETH): 0xa6f63fcb… 

 Stolen funds have mostly been deposited to Tornado Cash, with approximately $1M of ETH remaining in the Ethereum address. The attacker’s account was funded from a Binance-labelled wallet, though the original source was allegedly another CEX , SimpleSwap.

 In his thread on the incident, Orion’s CEO Alexey Koloskov stated his confidence in his own team’s code: 

 We have reasons to believe that the issue was not a result of any shortcomings in our core protocol code, but rather might have been caused by a vulnerability in mixing third-party libraries in one of the smart contracts used by our experimental and private brokers.

 But when such large amounts of money are on the line, security must be considered at all levels of a project’s stack.

 And it appears that this $3M loss has motivated Orion to take a more controlled approach:

 Moving forward, any and all contracts will be developed in-house to eliminate any potential vulnerabilities from third-party libraries. Our focus is to fortify the Orion Protocol and make sure it remains robust.

 Glad to hear Orion will be taking security more Sirius-ly. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
