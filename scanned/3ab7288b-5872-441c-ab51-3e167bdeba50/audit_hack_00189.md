# [C] Orbit Bridge exploit: It wasn’t just fireworks blowing up on New Year’s Eve

## Summary
Severity: Critical
Target: Orbit Bridge
Loss: $81,500,000
Published: 12/31/2023
Source: https://rekt.news/orbit-bridge-rekt
Type: rekt-postmortem

## Details
## Orbit Bridge - REKT

 Wednesday, January 3, 2024 Orbit Bridge - Bridge - REKT 

 read this article also in : 

 It wasn’t just fireworks blowing up on New Year’s Eve. 

 The final hours of 2023 saw Orbit Chain’s Ethereum bridge lose $81.5M to what looks to have been a compromised multisig. 

 Not to be confused with Orbiter, which connects ETH L2s, Orbit Chain is a standalone network aiming to work as a hub between other established ecosystems.

 The attack began just after 9PM UTC, and the alarm was raised just a few minutes later. 

 The official acknowledgement referenced a breach shortly before the transactions began…

 An unidentified access to Orbit Bridge, a decentralized Cross-chain protocol, was confirmed on Dec-31-2023 08:52:47 PM +UTC.

 …and was accompanied by warnings about opportunistic phishing attacks.

 With 2023 ending on a bit of a downer, for Orbit at least, what will 2024 bring? 

 Credit: Tayvano , Peckshield 

 While the hack is initially assumed to be due to compromised keys of signer-addresses on the Orbit’s ETH Vault multisig, the team is yet to disclose the exact nature of the attack vector.

 Others have suggested there could be a tx replay bug at play, similar to a ‘known issue’ identified during Theori’s audit (see page 7). 

 NOTE: This article will be updated to include the root cause once an official post-mortem has been published. 

 Follow-up note: On the 25th Jan, Ozys (Orbit's development company) published a statement implicating the firm's former CISO: 

 Two days after his voluntary retirement decision (November 20), the information security specialist who led Ozys’ efforts to become an ISMS-certified organization, abruptly made the firewall vulnerable and left the company on December 6, without any verbal or written communication during the handover process. 

 Investigations are ongoing. 

 Withdrawals began with 10M DAI at 21:08 UTC, followed by 231 WBTC ($9.8M), 9500 ETH ($21.5M), 10M USDC and finishing with 30M USDT at 21:25 UTC. The bridge was deactivated at 22:21 UTC.

 Centralised stables and WBTC were swapped out for ETH, as shown in Peckshield’s attack flow :

 Tay’s thread contains a full list of attacker addresses, where funds remain. 

 Attacker’s primary address: 0x9263e7873613ddc598a701709875634819176aff 

 The methodical tx pattern suggests this may be another Lazarus job, and the team has links to previous hacked projects Belt and Klayswap . 

 The attacker’s address was funded via Tornado Cash through an intermediary address . 

 Over half of Orbit Bridge’s TVL was drained in the attack, adding over $80M to an already impressive total for the presumed culprits. 

 Lazarus was responsible for at least $250M of losses in 2023 alone, with attacks on Atomic Wallet , AlphaPo , Stake and CoinEx all attributed to the group.

 As markets pick up and institutional interest in crypto continues to grow, we will have to take security more seriously if we want to be taken seriously ourselves:

 Looks like 2024 is going to be another year of handing DPRK billions of dollars on a silver platter. 🙄

 embarrassing af.

 Gradually emerging from a brutal bear market, will we simply ape into whatever the next narrative is, content to take on more and more risk as the potential rewards stack up?

 Or can we do better this year? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
