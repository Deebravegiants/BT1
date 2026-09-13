# [M] Hedera exploit: A nebulous threat rattled the entire Hedera ecosystem, yesterday

## Summary
Severity: Medium
Target: Hedera
Loss: $515,000
Published: 03/09/2023
Source: https://rekt.news/hedera-rekt
Type: rekt-postmortem

## Details
## Hedera - REKT

 Friday, March 10, 2023 Hedera - Ecosystem - REKT 

 read this article also in : zh 

 A nebulous threat rattled the entire Hedera ecosystem, yesterday. 

 Fear, rumour and suspicion took hold as both users and devs attempted to make sense of the chaos. 

 The “ proof-of-stake public ledger ”, built on blockchain-alternative Hashgraph , saw its TVL plunge by a third since the attack, from $36.8M to $24.6M.

 The HBAR Foundation announced “ network irregularities ” and, given the widespread nature of the attack, users frantically sought a safe haven for their funds.

 Dapps from across the network were affected, including AMMs Pangolin and Heliswap . After an initial panic , the larger SaucerSwap stated that their users had not been affected. The Hashport bridge was deactivated in response to the attack.

 The lack of certainty caused chaos, and what turned out to be around $515k stolen by the attacker, turned into $12M of damage to the ecosystem. 

 Later, Hedera announced it would be “ turning off network proxies on mainnet, making it inaccessible ” to users. At the time of writing, Hedera remains down while investigations continue.

 When will users get some clarity? 

 Details remain scant on exactly how the exploit worked, however, it is clear that the issue was in the network’s Smart Contract Service code. 

 In a Twitter thread, Hedera explained that “ The attacker targeted accounts used as liquidity pools on multiple DEXs that use Uniswap v2-derived contract code ported over to use the Hedera Token Service ”. HTS was audited by FP Complete in 2021.

 The head of Pangolin published a preliminary writeup which states the teams believed that the exploit was “ only affecting Hashport tokens. This proved to be false. Further investigation revealed all hts [Hedera Token Service] tokens were at risk ”.

 This allowed the attacker to burn bridged/wrapped tokens, as well as remove LP positions from the affected DEXs. According to the report, some funds were bridged back to ETH, after the Hashport team deactivated the bridge, the attacker turned to CEXs.

 Attacker’s address: https://hashscan.io/mainnet/account/0.0.2015717?p2=1 

 The report puts losses from Pangolin at $120k. HeliSwap lost just $2K, according to their rundown of events.

 The attacker’s alleged addresses contain a total of around $515k; ~$60k of HBAR and $280k of HTS stablecoins on Hedera , and $175k of ETH on Ethereum .

 Despite the news, the network’s native token, HBAR , lost less than the rest of the (currently tanking) market. 

 In an industry known for its frequency of multimillion dollar hacks, striking a balance between a clear warning and sowing panic is tricky. 

 Especially following the MyAlgo wallet-draining fiasco last week, the realisation that this incident was not contained to any one protocol was bound to cause chaos.

 While the pausing of the chain may have saved some user funds, it’s a worrying move which damages claims of legitimacy as a DeFi platform.

 One look at Hedera’s “ decentralized and transparent governing body ” gives an idea of the kind of organisations involved. The likes of Boeing, Dell and Ubisoft don’t strike us as hardcore DeFi idealogues.

 We may see some clarity over the next few days as to the exact mechanism of the exploit, but the damage has likely been done.

 DeFi users spook easily… 

 …and with good reason . 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
