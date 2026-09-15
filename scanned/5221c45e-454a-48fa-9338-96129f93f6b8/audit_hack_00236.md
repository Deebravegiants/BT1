# [H] Shibarium Bridge exploit: A botched launch of Shiba Inu’s ETH L2, Shibarium, sees a total of $2.6M of user funds stuck in a faulty bridge

## Summary
Severity: High
Target: Shibarium Bridge
Loss: $2,600,000
Published: 08/17/2023
Source: https://rekt.news/shibarium-bridge-rekt
Type: rekt-postmortem

## Details
## Shibarium Bridge - REKT

 Thursday, August 17, 2023 Shibarium - Bridge - REKT 

 read this article also in : 

 The Shibarium devs are in the doghouse. 

 A botched launch of Shiba Inu’s ETH L2, Shibarium, sees a total of $2.6M of user funds stuck in a faulty bridge. 

 As if there weren’t already enough ways to get rekt trading memecoins... 

 For some reason, the dog token needed an L2 where loyal holders could participate in canine-themed DeFi, GameFi, NFTs and general degeneracy, playing fetch with tickers such as BONE , LEASH (both down ~30%) and TREAT (not yet released).

 But shortly after launch, transactions stalled, and SHIB dropped almost 10% on the news that the chain had stopped producing blocks.

 We fucked up hard, we can’t recover the ETH bridged. 

 Or can they? 

 Given Shibarium isn’t producing blocks , withdrawals from the bridge cannot be initiated from the L2 side. 

 The contracts hold 1008 ETH ($1.8M) and 635k BONE ($774k), Shibarium’s gas token, at the time of writing, with deposits continuing long after the word got out.

 Bridge address (ETH): 0xc3897302ab4b42931cb4857050fa60f53b775870 

 Bridge address (BONE): 0x885fcE983b6a01633f764325B8c3c5D31032C995 

 However, it appears that not all hope is lost… 

 Given the bridges are proxy contracts, the funds should be recoverable, as pcaversaccio points out: 

 There is certainly a way to recover the ETH as long as the proxy owner didn't lose the private key. Upgrade the implementation, recover the funds via an ownable function, and set up a claim contract. And yes, upgradeability is still a bug as u see here🙃.

 Apparently, every dog has its day...

 "ALL IS WELL" claims the latest Shib Blog post , also stating that the screenshot about the funds being lost was fake. 

 While this may not be an irreparable mistake, it hopefully serves as a cautionary tale to anyone thinking that memecoins should be treated as anything other than memecoins… 

 In other bridge news, Thorchain was paused following disclosure of a bug in production, with a patch expected within 24-48 hrs, according to the team. 

 The project has featured on rekt.news twice , both in July 2021, with a spillover scam affecting RUNE holders thanks to a vulnerability in the token’s design.

 Thankfully, this time it’s a near-miss and not a leaderboard entry. 

 Bridges are a necessary evil for users wanting to explore the cryptoverse, and remain the most delicate pillar of the industry.

 Given the risk bottleneck they present, if they’re going to be built, they better be built right. 

 …and for a good reason. 

 The latest generation of memecoins have forced earlier examples into evolving. 

 But… why ? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
