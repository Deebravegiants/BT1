# [H] DeltaPrime exploit: DeltaPrime Blue on Arbitrum suffers $5.98 million loss in private key compromise

## Summary
Severity: High
Target: DeltaPrime
Loss: $5,980,000
Published: 09/15/2024
Source: https://rekt.news/deltaprime-rekt
Type: rekt-postmortem

## Details
## DeltaPrime - Rekt

 Monday, September 16, 2024 DeltaPrime - REKT 

 read this article also in : zh 

 Another day, another private key compromise. 

 DeltaPrime Blue on Arbitrum suffers $5.98 million loss in private key compromise. 

 Seems like DeltaPrime's vision of the future doesn't include robust key management.

 Whispers of a notorious nation-state hacker group are already circulating through the cryptosphere.

 Could the infamous Lazarus Group be behind this precision strike?

 While DeltaPrime scrambles to reassure users, questions loom. 

 Could we be entering a new era of state-sponsored hacks exploiting protocols caught with their pants down? 

 Credit: Chaofan Shou , DeltaPrime , Hacken , ZachXBT 
 The DeltaPrime drama unfolded like a well-rehearsed heist movie, with the attacker playing the role of a digital Danny Ocean. 

 According to first responder, Chaofan Shou , a compromised admin address on Arbitrum was used to upgrade DeltaPrime's proxy contracts to a malicious contract.

 Compromised Admin Address: 
 0x40E4172e595Fb5B3076dC6d0A1a24d885b881Afb 

 DeltaPrime’s Compromised Proxy Admin Address: 

 0xd550cfeA0BFFDC81B2dEe7B6d915D9D9e31d83A2 

 This nefarious upgrade allowed the attacker to artificially inflate their own deposit amounts across all pools. Talk about cooking the books.

 DeltaPrime, in a stunning display of captain obvious energy, acknowledged the loss , confirming the root cause to be a private key compromise.

 But let's dive deeper into this rabbit hole, courtesy of Hacken's breakdown . 

 For the Opening Act: Our digital Danny received 0.19 ETH for gas fees, funded via Across Protocol . Even hackers need to fuel up.

 Funding Transaction: 0xeb034ecfa6b1eaa95bc659883eff8a106fd5d7262da54848525f656597f55d3f 

 Setting the Stage: The attacker deployed their malicious proxy contract. The trap was set.

 Malicious Proxy Contract: 
 0xD4CA224a176A59ed1a346FA86C3e921e01659E73 

 The Main Event: The upgrading spree began. Five proxy contracts were upgraded with malicious implementations in just 8 confirmed blocks. Efficiency at its finest, folks.

 First Upgrade Transaction: 0x2e6748e92e4f833d3ea3c2aa7d11e74aa502e2cfcab8398dc2056a83a1b7caae 

 The First Withdrawal: Barely seconds after the upgrades, 2.44M USDC vanished. Talk about not letting the ink dry.

 First Withdrawal Transaction: 0x28a9b62fbfc375ebb3f5321d80baac9c2a225a6ec2f140cbfae5bff95fc80b1e 

 Our hacker didn't discriminate, hitting multiple contracts like a kid in a candy store: 

 DeltaPrimeWrappedETH: 
 0x0bebeb5679115f143772cfd97359bbcc393d46b3 

 USDCPoolTUP: 

 0x8FE3842e0B7472a57f2A2D56cF6bCe08517A1De0 

 DeltaPrimeArbitrum: 
 0x2B8C610F3fC6F883817637d15514293565C3d08A 

 DeltaPrimeBitcoin: 
 0x5CdE36c23f0909960BA4D6E8713257C6191f8C35 

 DaiPoolTUP: 

 0xd5E8f691756c3d7b86FD8A89A06497D38D362540 

 In a dizzying display of greed (or thoroughness, depending on your perspective), a total of 57 withdrawals were executed. 

 The grand finale came with the attacker riding off into the sunrise with their ill-gotten gains.

 The loot bag? A mix of USDC, WBTC, and WETH – all swiftly swapped to ETH.

 Because who doesn't love a good money laundering challenge?

 As a parting gift , the Proxy Admin was changed on all victim contracts. Locking the barn door after the horse has bolted, attacker edition. 

 DeltaPrime claims their Avalanche deployment is safe , tucked away behind multisigs and cold wallets. 

 Cold comfort for the Arbitrum users left out in the cold, wouldn't you say?

 The team promises that "the insurance pool will cover any potential losses where possible/necessary."

 DeltaPrime was audited several times , but no amount of code scrutiny can catch a leaked private key.

 Auditors cannot audit human error.

 The attacker's loot currently sits untouched, a $5.98 million middle finger to DeltaPrime and the wider DeFi community.

 Here's where things get spicy. Our favorite blockchain sleuth, ZachXBT, dropped a possible tantalizing hint : 

 "Idk if related but they were one of the teams with the DPRK IT workers I reached out to warn (was told they were all removed)." 

 Could this be more than just a garden-variety hack?

 Are we looking at the handiwork of the infamous Lazarus Group?

 The plot thickens faster than a badly coded smart contract.

 DeltaPrime serves as yet another stark reminder in DeFi, your protocol's security is only as strong as your weakest private key – and your team's ability to keep it private. 

 In this current era of digital heists, are we watching the evolution of crime or the devolution of security? 

 DeltaPrime's $5.98 million stumble exposes the fragile underbelly of DeFi's grand ambitions. 

 A single compromised key, and poof – millions vanish faster than you can say "Defi." 

 The Lazarus Group whispers add a spicy geopolitical flavor to this already pungent dish of incompetence.

 As DeltaPrime scrambles to plug the holes in their sinking ship, users are left treading water, clinging to promises of insurance and cold comfort.

 This hack serves as another brutal wake-up call.

 In the world of DeFi, your protocol is one leaked private key away from becoming a cautionary tale.

 With nation-state actors potentially entering the fray, are we witnessing the birth of financial warfare 2.0? 

 Or is this just the same old story of greed and incompetence, now with a shiny new blockchain bow? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
