# [H] GemPad exploit: Missing reentrancy guards turned GemPad's secure lock box into a perfect heist target

## Summary
Severity: High
Target: GemPad
Loss: $1,900,000
Published: 12/17/2024
Source: https://rekt.news/gempad-rekt
Type: rekt-postmortem

## Details
## GemPad - Rekt

 Tuesday, December 17, 2024 GemPad - Reentrancy - Rekt 

 read this article also in : 

 Missing reentrancy guards turned GemPad's secure lock box into a perfect heist target. 

 What started as a quiet night across Ethereum, BNB Chain, and Base networks exploded into chaos, as roughly $1.9 million worth of locked tokens found an unauthorized exit. 

 Several projects watched helplessly as their supposedly secured assets slipped through GemPad's fingers, victims of DeFi's most notorious exploit pattern.

 BPay, Munch, Nutcoin, and others scrambled to calm their communities while GemPad raced to patch the vulnerability.

 The protocol swiftly acknowledged the breach and began working with affected projects, but their stolen liquidity had already scattered across chains. 

 How many more protocols need to learn that security isn't just about having locks, but making sure they actually work? 

 Credit: OkLink , GemPad , Cyvers Alerts , pennyplayer , BPay , Munch Protocol , AnonFi , NutCoin , FOMO , LOA , Hemera Trading , Dub Token , Alien Base 
 Sometimes the most devastating flaws hide in plain sight, waiting for the right pair of eyes to notice them. 

 Like a jeweler examining a suspect gem, scrutiny reveals what casual glances miss.

 OKLink's vigilant team first caught the sparkle of something wrong – multiple protocols bleeding liquidity through the same flaw.

 Their analysis revealed a critical oversight in GemPad's lock contract: missing reentrancy protection on the withdrawal function, leaving locked assets vulnerable to a classic sleight of hand.

 GemPad confirmed the exploit soon after , acknowledging their security locks had been breached and immediately began working with security partners to investigate. 

 Cyvers Alerts later confirmed the scope of the attack, tracking the draining of digital assets across multiple chains as the attacker methodically emptied one lock box after another. 

 Pennyplayer's analysis revealed the elegant simplicity of the attack: a classic reentrancy exploit targeting the collectFees function.

 The attacker crafted malicious tokens that triggered callbacks during transfers, creating LP locks essentially for free.

 With each reentrant call, they could withdraw the locked LP amount, turning GemPad's security mechanism against itself. 

 Attack transactions by Blocksec

 Attacker address on Mainnet: 

 0xFDd9b0A7e7e16b5Fd48a3D1e242aF362bC81bCaa 

 Attacker address on BSC: 

 0xFDd9b0A7e7e16b5Fd48a3D1e242aF362bC81bCaa 

 Attacker address on Base: 

 0xFDd9b0A7e7e16b5Fd48a3D1e242aF362bC81bCaa 

 Attack Contract on Mainnet: 

 0x8e18Fb32061600A82225CAbD7fecF5b1be477c43 

 Attack Contract on BSC: 

 0x8e18Fb32061600A82225CAbD7fecF5b1be477c43 

 Attack Contract on Base: 

 0x8e18Fb32061600A82225CAbD7fecF5b1be477c43 

 While Base chain still holds a portion of the stolen funds, the rest have already vanished into crypto's favorite mixing service – another digital heist dissolving into the blockchain. 

 The casualties stacked up quickly. BPay and Munch Protocol watched their liquidity vanish, while AnonFi halted all token trading. 

 Nutcoin's team demanded answers as their locks were drained, and FOMO Network could only watch as their pools emptied.

 The Law of Attraction Coin and Hemera Trading AI scrambled to calm their communities, while Dub Token faced the ripple effects through Alien Base's ALB/DUB farm .

 GemPad's approach to security painted an interesting picture. 

 Their platform offered a no-code token creation system - five pre-audited templates ranging from Simple to Ultimate, each with ContractWolf's stamp of approval. 

 Projects could point, click, and launch their token without touching a line of code .

 While democratizing token creation might have been the goal, this plug-and-play approach to security proved meaningless when the underlying lock mechanism failed.

 While pre-audited templates might make token creation accessible to all, they mean nothing if the foundation beneath them crumbles. 

 When one lock breaks and several protocols fall, how many more dominoes are silently waiting their turn? 

 Missing reentrancy guards turned a trusted vault into a systemic cascade of failures. 

 Projects rushing to secure their assets behind GemPad's locks found themselves victims of crypto's oldest exploit pattern. 

 Audited templates and no-code solutions promised security through simplicity, yet failed to protect against a vulnerability as old as DeFi itself.

 Multiple protocols learned the hard way that outsourcing security doesn't mean outsourcing responsibility.

 GemPad's swift response and commitment to affected projects shows promise, but their reputation as a trusted platform now hangs by a thread.

 Teams building on borrowed trust might want to check their foundations before the next domino starts to wobble. 

 Your lock box provider just got their locks picked – still feeling secure about those custody solutions? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
