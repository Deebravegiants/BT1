# [H] Audius exploit: Audius, web3’s answer to Spotify, has fallen victim to a governance attack, losing $6M of its native token, AUDIO

## Summary
Severity: High
Target: Audius
Loss: $6,000,000
Published: 07/23/2022
Source: https://rekt.news/audius-rekt
Type: rekt-postmortem

## Details
## Audius - REKT

 Monday, July 25, 2022 Audius - REKT 

 read this article also in : zh 

 Audius, web3’s answer to Spotify, has fallen victim to a governance attack, losing $6M of its native token, AUDIO. 

 The attacker passed a malicious proposal transferring the funds directly from the treasury before dumping them onto the market for just ~$1M.

 AUDIO is used for user rewards and artist tips, as well as for governance purposes on the music-streaming service. 

 Shortly after the alarm was raised , Audius announced the “ unauthorized transfer ”, whilst asking for help with the investigation: “ If you'd like to help our response team, please reach out. ”

 Pause, rewind, play… 

 Credit: Audius , Spreek 

 According to the official post mortem , the attacker was able to reinitialise governance contracts, delegating a large number of governance tokens to themself and bypassing safeguards meant to limit malicious proposals. 

 Then, with their vastly increased voting power, they could pass a proposal to transfer 18M AUDIO tokens out of the treasury and straight to their own address. 

 Audius uses AudiusAdminUpgradabilityProxy to make any upgrades to the governance contracts. The proxyAdmin address is set as the address of the main governance contract , in storage slot 0.

 However, this creates a collision with OpenZeppelin's Initializable contract , leading to a bug which allowed the attacker to take control of the governance contract and change parameters on any of Audius’ Governance, Staking & DelegateManagerV2 contracts.

 For further details, see OpenZeppelin docs on storage collisions. 

 The post mortem summarises the actions of the attacker as follows: 

 With this, the attacker was able to (1) Re-define voting on the Audius protocol and modify the governance contract’s guardian address (2) Set the governance address of both the Staking & DelegateManagerV2 contracts to that of a custom deployment of the Audius governance contract 0xbdbb5945f252bc3466a319cdcc3ee8056bf2e569) and abuse the Audius protocol by

 Mark an erroneous delegation of 10,000,000,000,000 $AUDIO to themselves in an attempt to pass a governance vote. (No circulating supply impact / confined to storage of Staking & Delegation contracts)

 Mark a second erroneous delegation of 10,000,000,000,000 $AUDIO to themselves in an attempt to pass a governance vote, which did pass and transferred the funds. (No circulating supply impact / confined to storage of Staking & Delegation contracts)

 Transferring 18,564,497 $AUDIO tokens from the community treasury: https://etherscan.io/tx/0x4227bca8ed4b8915c7eec0e14ad3748a88c4371d4176e716e8007249b9980dc9 

 Attacker’s address: 0xa0c7BD318D69424603CBf91e9969870F21B8ab4c 

 The attacker then went on to dump the AUDIO in a single transaction via Uniswap v2, incurring major slippage and making off with just 704 ETH (~$1M).

 The funds were then deposited into Tornado Cash around 10 hours later.

 Despite the extreme price action as the attacker dumped the loot, the price of AUDIO has held up well since the incident.

 A quick response time from the team (plus help ), and the loss coming from the treasury, rather than users pockets, likely minimised the fallout.

 The contracts had been audited twice, by Kudelski and OpenZeppelin , and the vulnerability is a known issue .

 However, this doesn’t look to have knocked Audius off the DeFi playlist for good.

 Let’s just hope their debut is a one-hit wonder. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
