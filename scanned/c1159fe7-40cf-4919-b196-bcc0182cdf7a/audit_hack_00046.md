# [C] BNB Bridge exploit: “Have you tried turning it off and on again?”

## Summary
Severity: Critical
Target: BNB Bridge
Loss: $586,000,000
Published: 10/06/2022
Source: https://rekt.news/bnb-bridge-rekt
Type: rekt-postmortem

## Details
## BNB Bridge - REKT

 Friday, October 7, 2022 BSC - Bridge - REKT 

 read this article also in : zh 

 “Have you tried turning it off and on again?” 

 2M BNB stolen in a hack as complex as Binance’s naming system. 

 BSC Token Hub, the BNB bridge between the old Binance Beacon Chain and BSC, now BNB Chain… was exploited into minting two lots of 1M BNB directly to the hacker’s address.

 With a BNB price of $293 at the time of the hack, the stolen 2M BNB amounts to $586M (#3 on the leaderboard). 

 However, the hacker managed to escape to other chains with just $127M before losing access to the rest of the funds.

 After noticing the “ irregular activity ”, DeFi’s 3rd largest L1 was paused for ~8 hours .

 However, what of all the users unable to access their own funds? 

 What of those who may have needed funds in an emergency, or were potentially facing liquidation as their positions were out of their reach… 

 ...for as long as Binance wanted. 

 In a now deleted tweet , CZ said “ It's not about cash flow; it's crypto flow. ” while the attack was underway…

 Credit: samczsun , FrankResearcher 

 The attacker exploited the BNB bridge into minting two batches of 1M BNB each, via falsified proofs of deposit on the legacy Binance Beacon Chain. The transactions occurred at 18:26 UTC and 20:43 UTC .

 The bridge uses vulnerable IAVL verification which the attacker was able to forge, specifically for block 110217401, from August 2020.

 Exploiter’s address: 0x489a8756c18c0b8b24ec2a2b9ff3d4d447f79bec 

 As samczsun put it:

 In summary, there was a bug in the way that the Binance Bridge verified proofs which could have allowed attackers to forge arbitrary messages. Fortunately, the attacker here only forged two messages, but the damage could have been far worse

 For a detailed explanation, see the full thread .

 Rather than dumping the BNB directly and drawing attention to the price action, funds were deposited as collateral on BSC lending platform Venus Protocol. Amidst the confusion, the Venus team were keen to point out that their protocol hadn’t suffered an exploit, although their users faced a spike in rates as borrow liquidity was withdrawn.

 The tactic of borrowing rather than dumping initially led some to believe that this may just be a gigawhale moving funds around. However, as users began to notice high-slippage swaps and Tether blacklisting funds , it became clear that this was something more sinister.

 Likely anticipating that Binance would halt the chain, the exploiter raced to find liquidity to bridge and move as much of the loot as possible to other chains. 

 SlowMist traced the movement of funds. First, the attacker supplied 900k BNB to Venus, borrowing a total of $147M in stablecoins, before bridging to Ethereum and L2s, Fantom (now making up over 10% of TVL ), Avalanche and Polygon networks.

 See SlowMist’s table below for a breakdown of the exploiter’s positions , including frozen USDT (totalling ~$6.5M).

 When the BNB team halted the chain, approximately 90 mins after the second transaction, the hacker lost access to the ~$430M still on their BSC address . The hacker’s addresses were initially funded from ChangeNOW exchange.

 Since the incident, Binance comms have gone into damage limitation mode. 

 An official update states that “decentralised chains are not designed to be stopped”. But with just “26 active validators”, does BNB chain qualify as decentralised in the first place?

 And was it ever, really, credibly decentralised? 

 The update also sets out some next steps, including governance votes to decide on whether to freeze or burn the stolen funds, and establishing Bug Bounty and whitehat bounty programmes.

 The number of “ community validators ” will also be increased in a “ move toward further decentralisation ” (or reduced responsibility).

 Covering the funds that found their way off-chain is a drop in the ocean for Binance. 

 And as CZ makes clear , his size is size: “The current impact estimate is around $100m USD equvilent, about a quarter of the last BNB burn.”

 However, the Binance CEO has also distanced himself from the incident, tweeting that he is “ not that involved in the technical side of BNB Chain. Far less than Vitalik with ETH. ” possibly attempting to convince any regulators looking for a DeFi scapegoat that their attentions should be directed elsewhere…

 If the chain could have been paused this time, why not for all the other BSC hacks we’ve covered? And how will this look in the eyes of regulators, now that it’s clear they’ve been in control the entire time…

 More importantly, though, a dangerous precedent has been set by pressing pause on such a heavily-used network. If we ever reach mass-adoption of crypto for day-to-day transactions, how could these acts be justified when chain halts could, ultimately, mean the difference between life and death?

 But, as this video from 2019 shows, CZ doesn’t regard the immutability of blockchains as sacrosanct. Although the plan never went ahead, he contemplates the rolling back of the Bitcoin network despite the “far reaching consequences” and risk of “destroying credibility”.

 Will BNB’s involvement in “DeFi” retain any credibility after today? 

 For now, though, it’s just another bridge exploit, and one more entry on the leaderboard . 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
