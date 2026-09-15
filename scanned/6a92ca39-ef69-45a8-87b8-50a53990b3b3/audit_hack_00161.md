# [H] Merlin DEX exploit: $1.8M disappeared in a puff of smoke as Merlin pulled the classic DeFi magic trick

## Summary
Severity: High
Target: Merlin DEX
Loss: $1,820,000
Published: 04/25/2023
Source: https://rekt.news/merlin-dex-rekt
Type: rekt-postmortem

## Details
## Merlin DEX - REKT

 Thursday, April 27, 2023 Merlin - zksync - Rugpull - REKT 

 read this article also in : zh 

 $1.8M disappeared in a puff of smoke as Merlin pulled the classic DeFi magic trick. 

 Merlin, a DEX native to the recently-launched zksync L2, was in the middle of a 3-day “ Liquidity Generation Event ” as part of its token (MAGE) launch.

 The alarm was initially raised by a community member before Peckshield spread the message. Merlin then acknowledged the incident, advising users to revoke permissions as a precaution.

 Not to be confused with three-time leaderboard entrant Merlin Labs (who got rekt on repeat during Spring 2021’s BSC bloodbath), Merlin had passed its second audit by Certik just two days before the attack.

 Merlin’s story may be that of a simple rug; a tale we’ve heard many times before. 

 But, this time, Merlin has inadvertently conjured a debate into the value of certain styles of audit… 

 Credit: BeosinAlert 

 The rug mechanism was a straightforward case of draining the liquidity pools into which users were depositing as part of the MAGE token sale.

 This was made possible via max approvals granted to the Feeto address upon deployment of the pools. The individual/s in control of the Feeto address could then drain the pool of all assets, which were then bridged to ETH.

 Merlin’s own post-mortem places the blame squarely on the back-end development team. The thread includes links to developers’ github profiles and states that Serbian authorities have been contacted.

 Attacker address (into which funds were drained): 0x2744d62a1e9ab975f4d77fe52e16206464ea79b7 

 See Beosin’s full analysis for further details and addresses. 

 The rugged funds were bridged back to Ethereum, swapped for ETH and transferred to other addresses.

 This is the first incident on zksync, a zero-knowledge Ethereum rollup whose mainnet launched in March. 

 It didn’t take long for the new environment to become a target… 

 zksync already had a close call when their Twitter handle was targeted (presumably to conduct a phishing campaign) earlier this month.

 As new ecosystems flourish, leveraging exciting tech to push our industry forward, bad actors will never be far behind. 

 And low-effort cash grabs make the perfect honeypot for those who would pull the rug on users or would-be hackers looking for vulnerable, hastily deployed code… 

 Generally, an audit by a reputable blockchain security firm is a good sign for those unsure whether or not to ape in. 

 But when some logos look less like a mark of quality and more like a red flag, what counts as ‘reputable’? 

 The very same day that their recently-approved project was drained, Certik’s founder boasted of their volume of bargain audits in the industry. 

 With Certik’s stamp of approval on so many rekt projects, many are casting doubts on the firm's value to the space.

 It should be noted that, in their initial audit , Certik did indeed bring up the issue of trust, recommending that the protocol take measures to sufficiently decentralise:

 We advise the client to carefully manage the privileged account's private key to avoid any potential risks of being hacked. In general, we strongly recommend centralized privileges or roles in the protocol be improved via a decentralized mechanism or smart-contract-based accounts with enhanced security practices, e.g., multisignature wallets.

 However, this issue was marked as ‘Resolved’ by Certik, who stated that the Merlin team had promised to use a multisig. Enough users apparently didn’t read the audit fully, or simply didn’t care about the implications of trusting the project.

 Facing further claims that the code includes an intentional backdoor, Certik is clearly feeling the heat. The firm is considering a “ community compensation plan ” to cover the losses. 

 Quick and dirty audits should not be deemed sufficient reassurance, especially for multimillion dollar protocols. Some personal responsibility is also necessary to stay safe… 

 Ruggers gonna rug. 

 And when many protocols have centralisation issues which could potentially lead to a rug, yet are overlooked by FOMO-ing apes and airdrop hunters … 

 Where does the blame really lie? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
