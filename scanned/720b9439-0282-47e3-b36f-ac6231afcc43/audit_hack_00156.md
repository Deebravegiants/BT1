# [H] MM Finance exploit: Mad Meerkat Finance (not to be confused with normal Meerkat Finance ) is in the hole, to the tune of $2M

## Summary
Severity: High
Target: MM Finance
Loss: $2,000,000
Published: 05/04/2022
Source: https://rekt.news/madmeerkat-finance-rekt
Type: rekt-postmortem

## Details
## MM Finance - REKT

 Friday, May 6, 2022 MM Finance - REKT 

 read this article also in : zh 

 Mad Meerkat Finance (not to be confused with normal Meerkat Finance ) is in the hole, to the tune of $2M. 

 The Cronos-based DEX had its front-end exploited , resulting in losses of over $2M for its users.

 Beginning around 7:30 PM on 4th of May, users swapping, adding or removing liquidity on the protocol had the output funds redirected straight into the attacker’s wallet.

 The exploit lasted for approximately 3 hours before the team took down the front-end.

 During the attack, team members in Discord advised users not to interact with the site.

 But why was the compromised site left up for so long? Why didn’t they block access? 

 It is unclear exactly how the attacker managed to gain access, and the official post mortem doesn’t give much away: 

 MM.finance site was the subject of a DNS attack earlier where an attacker managed to inject a malicious contract address into the frontend code. Attacker used a DNS vulnerability to modify the router contract address in our hosted files.

 This led to some speculation in the rekt.news telegram group , with users contemplating whether the exploit had redirected users to a cloned version of the page.

 “hmm - looks like it was actually a dns redirect possibly…”
“ people are saying bad SSL certificate”

 While others were more skeptical . 

 Some users raised their concerns via Discord , but were not taken seriously by the team.

 Whatever the attack vector, the exploit was prepared, exposing users’ transactions to a malicious router linked to the attacker’s address. 

 Then, beginning with this swap at 19:28:35 PM +UTC, the outputs of all interactions with the DEX were rerouted to the attacker’s address .

 600+ transactions were rerouted in this way, with the profits being swapped to USDT and bridged back to Ethereum before being deposited (743 ETH so far) into Tornado Cash.

 The post-mortem advises users to double check for the correct router address (0x145677FC4d9b8F19B5D56d1820c48e0443049a30) during transaction confirmations. 

 Another mongoose playing fast and loose with their operational security. 

 The Mad Meerkat team have traced the attacker’s financing back to OKX, and are appealing for help in determining the hacker’s identity.

 The affected users will be reimbursed via the team’s share of trading fees. Further details on the compensation package can be found here .

 This will be the first exploit on Cronos to go onto our leaderboard , with a lowly entry of #76.

 Front-end attacks, back-end attacks, when will we reach the end of the attacks? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
