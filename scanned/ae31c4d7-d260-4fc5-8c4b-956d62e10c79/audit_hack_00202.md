# [H] Polter Finance exploit: When will they learn that "fork and pray" isn't a security strategy?

## Summary
Severity: High
Target: Polter Finance
Loss: $8,700,000
Published: 11/16/2024
Source: https://rekt.news/polter-finance-rekt
Type: rekt-postmortem

## Details
## Polter Finance

 Monday, November 18, 2024 Polter Finance - Rekt 

 read this article also in : 

 When will they learn that "fork and pray" isn't a security strategy? 

 Polter Finance, the latest victim in DeFi's parade of recklessness, lost roughly $8.7 million when their unaudited protocol met a classic price manipulation attack. 

 Their newly launched BOO market proved to be more trick than treat, as an attacker turned spot price dependencies into their personal ATM.

 The team's response was a masterclass in damage control theater - filing a possibly inflated $12 million police report while their TVL bled out through a painfully predictable oracle exploit.

 Like a crypto soap opera, we watched the familiar scenes unfold: platform pause, bridge notifications, Binance wallet traces, and the obligatory "dear ser hacker" negotiation attempts.

 Another day, another protocol learning that copying code doesn't copy security. 

 But who needs audits when you have optimism? 

 Credit: whichghost , BcPaintball , Polter Finance , William Li , Nick Franklin 
 Turns out BOO markets can haunt you. 

 BcPaintball first spotted the ghost in the machine, reporting suspicious activity on Polter's newly launched BOO market.

 The team, perhaps too busy counting their unaudited chickens , took roughly 7 hours to acknowledge what was already painfully obvious to everyone else.

 Nick Franklin's autopsy revealed a textbook case of oracle manipulation - proving yet again that spot prices make better victims than oracles.

 William Li's initial analysis pointed to what looked like an "empty market" rounding error, but deeper investigation exposed something far more fundamental - a faulty oracle implementation that practically begged to be exploited. 

 The protocol's critical mistake? Trusting SpookySwap V2/V3 pool prices for their BOO token oracle - about as secure as using a paper lock on a bank vault. 

 By draining the BOO token reserves through a flash loan, the attacker manipulated the price feed like a puppeteer with particularly profitable strings.

 One BOO deposit was all it took to borrow against artificially inflated collateral, proving that in DeFi, sometimes the simplest tricks are the most expensive.

 Exploiter: 
 0x511f427Cdf0c4e463655856db382E05D79Ac44a6 

 Exploiter contract: 
 0xA21451aC32372C123191B3a4FC01deB69F91533a 

 Flow of Funds on Metasleuth . 

 The team's post-exploit performance deserves its own review. 

 Hours after watching roughly $8.7 million evaporate, they filed a police report claiming $12 million in losses - perhaps hoping inflation would make up the difference. 

 The team's crisis management playbook rolled out with clockwork predictability.

 Within hours, they'd paused the platform, notified bridges, and claimed to have traced the exploiter's wallet to Binance - though blockchain analysis suggests the funds had already begun their journey through different paths.

 "Platform paused soon after the exploit was identified. Bridges were notified. We identified wallets involved and traced it to Binance," announced the Polter team, punctuating their statement with the DeFi equivalent of "thoughts and prayers" - a promise to contact authorities.

 Like a jilted lover sliding into DMs, Polter took to the blockchain to negotiate - though perhaps their time would've been better spent sliding into auditors' inboxes months ago. 

 In the grand tradition of "move fast and break things," Polter Finance skipped the tedious business of security audits entirely . Their confidence in unaudited code proved almost as inflated as their BOO token prices. 

 "As the smart contract used is identical to Geist, except for the removal of the flash-loan function in Lending Pool, we are providing the Geist audit report here" - proclaims Polter's audit page , demonstrating the kind of security theater that gives Broadway a run for its money.

 The aftermath serves as yet another case study in the false economy of skipping audits. Close to $8.7 million lost to save what - a few weeks and a few thousand dollars?

 But who needs professional security reviews when you can CTRL+C CTRL+V your way to launch?

 The only audit they got was from the exploiter - and those results just came in.

 Crypto may be rocketing into the mainstream, but unless protocols like Polter start getting their act together, it’s more likely to crash and burn before it ever reaches the moon.

 The industry's growing pains are already painful enough, and without addressing these basic security flaws, mainstream adoption could end up being a full-speed disaster. 

 Anyone else think Polter won’t stick around for the full ride? 

 Another day, another protocol proving that copying code doesn't equal competence. 

 Polter Finance's roughly $8.7 million lesson in basic oracle security came with extra credit in creative accounting - their $12 million police report suggesting they're better at inflating numbers than securing them. 

 From skipping audits to serving up manipulatable oracles on a silver platter, the team demonstrated a masterclass in "how not to run a DeFi protocol."

 Their security strategy amounted to little more than hopes, prayers, and someone else's audit report.

 The exploiter didn't discover a novel vulnerability - they simply walked through the front door Polter left wide open.

 In crypto's current surge toward mainstream adoption, such amateur-hour security practices aren't just embarrassing - they're dangerous.

 Polter now takes its place among the countless protocols that mistook convenience for competence. 

 But here's the real haunting question - how many more users need to get rekt before protocols realize that copy pasta code doesn't make you ready for primetime? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
