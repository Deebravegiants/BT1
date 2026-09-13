# [C] Multichain exploit: Multichain addresses were drained yesterday for a total of $126M, representing around 50% of the FTM bridge and 80% of the Moonriver bridge holdings

## Summary
Severity: Critical
Target: Multichain
Loss: $126,300,000
Published: 07/06/2023
Source: https://rekt.news/multichain-rekt2
Type: rekt-postmortem

## Details
## Multichain - REKT 2

 Friday, July 7, 2023 Multichain - Bridge - REKT 

 read this article also in : 

 Multi-rekt. 

 Multichain addresses were drained yesterday for a total of $126M, representing around 50% of the FTM bridge and 80% of the Moonriver bridge holdings. 

 The project has quite the record… 

 Before re-branding to Multichain, Anyswap was hacked for $8M almost two years ago.

 Then, in early 2022, six multi-token contracts were found to be vulnerable to an approvals draining attack , estimated to have led to $3M in user losses.

 Finally, in May of this year, Multichain caused panic when responding to bridging delays, potential insider dumping and team arrest rumours, explaining things away with a vague, but foreboding, “ force majeure ”.

 This time, comms were equally worrying: 

 The lockup assets on the Multichain MPC address have been moved to an unknown address abnormally.

 The team is not sure what happened and is currently investigating.

 It is recommended that all users suspend the use of Multichain services and revoke all contract approvals related to Multichain. 

 Fantom, which is heavily reliant on Multichain versions of many non-native assets (USDC, USDT, DAI, wETH and wBTC), also didn’t have any answers .

 With such a long and chequered history, and still no definitive root cause identified by the team… 

 Is this just another of Cronje’s test-in-prod experiments gone wrong? 

 The largest rug we’ve ever seen? 

 Or even a very shy whitehat? 

 Credit: Beosin 

 As the large withdrawals picked up attention on Twitter, an initial theory that the withdrawals were related to Stargate/LayerZero’s launch of new offerings on FTM were quickly put to bed by the LZ team.

 While the exact attack vector is still to be determined, the behaviour of transactions appear to suggest that an attacker was able to control the addresses directly. 

 Plausible methods of gaining access include a back-end breach, obtaining private keys via spearphishing or the actions of a malicious insider.

 The last time Multichain (then Anyswap) was hacked, the attacker was able to back-calculate private keys from repeated transaction data the (then recently-launched) v3. 

 Exploiter addresses and current holdings at time of writing (total $126.3M): 

 0x9d5765ae1c95c21d4cc3b1d5bba71bad3b012b68 ($16.7M including DAI, LINK, USDT and CRV)

 0xefeef8e968a0db92781ac7b3b7c821909ef10c88 ($30.1M in USDC)

 0x418ed2554c010a0c63024d1da3a93b4dc26e5bb7 ($13.4M in wETH)

 0x622e5f32e9ed5318d3a05ee2932fd3e118347ba0 ($30.9M in wBTC)

 0x48bead89e696ee93b04913cb0006f35adb844537 ($7.5M in USDC, USDT, DAI and wBTC from Moonriver)

 0x027f1571aca57354223276722dc7b572a5b05cd8 ($27.7M in USDC)

 The full list of assets can be found here . 

 While the losses are enormous, funds have not been swapped or moved since being drained, potentially pointing to actions of a whitehat. Additionally, over half the amount ($65M) could be frozen by Tether and Circle.

 Two bridges have earned their 2nd leaderboard entry in a week, after Poly Network’s multisig was compromised last Saturday. 

 The latest in an ongoing series of bridge hacks, this is another reminder of Vitalik’s warning that, despite the name of today's entry, a multi- not cross-chain future may be the safest way to go for crypto.

 As we wrote after the >$300M Wormhole hack:

 In the race across the cryptoverse to reach experimental and more lucrative opportunities, many are willing to trust in newer tech. But when one of these gateways fails, the damage done can be immense.

 Once again, another project linked to Cronje’s decentralised monopoly has ended up rekt, joining many others on the leaderboard, some with multiple entries . 

 How many more victims will lose out to these ‘experiments’? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
