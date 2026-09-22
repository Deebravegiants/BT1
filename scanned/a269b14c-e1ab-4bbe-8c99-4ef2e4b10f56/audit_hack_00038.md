# [H] Bedrock exploit: Bedrock just got a lesson in why you should always double-check your math homework

## Summary
Severity: High
Target: Bedrock
Loss: $2,000,000
Published: 09/25/2024
Source: https://rekt.news/bedrock-rekt
Type: rekt-postmortem

## Details
## Bedrock - Rekt

 Monday, September 30, 2024 Bedrock - REKT 

 read this article also in : zh 

 Bedrock just got a lesson in why you should always double-check your math homework. 

 In a twist that would make even a quantum physicist's head spin, their uniBTC vault decided to play fast and loose with exchange rates, turning Ethereum deposits into a Bitcoin bonanza. 

 This digital alchemy managed to transmute $2 million into thin air bon September 25th, before anyone could say "smart contract audit."

 The vulnerability, spread across 8 blockchain networks like a particularly virulent strain of crypto-pox, allowed users to mint uniBTC faster than a money printer on steroids. 

 In the aftermath of yet another DeFi debacle, we're left pondering: when "code is law" fails, does it default to "finders, keepers"? 

 Credit: Dedaub , Bedrock 
 In the high-stakes game of DeFi whack-a-mole, Dedaub just scored a critical hit. 

 These code sleuths uncovered a ticking time bomb in Bedrock's uniBTC vault contracts - a vulnerability so juicy it practically had dollar signs for eyes.

 We're talking about a $75 million treasure chest spread across at least 8 different chains, just waiting for someone to pick the lock.

 Dedaub, channeling their inner Paul Revere, didn't waste time.

 They fired off alerts to Bedrock on Twitter and speed-dialed SEAL 911, all while the crypto world slumbered, blissfully unaware of the impending chaos. 

 But in the world of DeFi, time waits for no dev. 

 While Bedrock's team was likely dreaming of lambos and tropical islands (or just, you know, sleeping), the vulnerability transformed from potential threat to actual disaster.

 A mere two hours after Dedaub's digital distress signal, the exploit hit.

 A swarm of opportunists, realized that Bedrock's smart contract was practically begging to be milked.

 The damage? A cool $2 million vanished faster than you can say "decentralized finance." 

 But here's the kicker - with uniBTC's $75 million market cap on Ethereum alone, this could have been just the tip of a very expensive iceberg. 

 As the blockchain detectives pieced together the digital crime scene, they found themselves staring at a vulnerability so basic, it would make a first-year coding student blush.

 According to the post mortem , the vulnerability in Bedrock's smart contracts was more complex than a simple miscalculation.

 At its core, the issue stemmed from a failure to properly handle native tokens on non-native BTC chains.

 The crux of the problem lay in the SigmaSupplier contract, which didn't register NATIVE_BTC. 

 This oversight caused the total supply to always register as zero, effectively neutering the caps restriction mechanism designed to prevent unauthorized minting. 

 With this safeguard unknowingly disabled, the Vault contract's checks were rendered toothless.

 The result? A wide-open door for users to mint uniBTC tokens using native tokens on non-native BTC chains - a process that should have been impossible by design.

 In essence, Bedrock's smart contracts were playing by the wrong rulebook, allowing users to mint uniBTC in ways the protocol never intended.

 It wasn't so much a mathematical error as a fundamental mishandling of token types and chain interactions.

 This mishandling opened the floodgates for a series of exploits across multiple chains. 

 The vulnerable vault contract deployed on September 25th , allowed an ETH to uniBTC exchange at a 1:1 rate. 

 In one brazen example, an attacker minted 30.8 uniBTC using 30.8 ETH and promptly sold 28.8 uniBTC for 27.8 WBTC in a single transaction.

 Exploiter Address: 

 0x2bFB373017349820dda2Da8230E6b66739BE9F96 

 Attack Transaction: 
 0x725f0d65340c859e0f64e72ca8260220c526c3e0ccde530004160809f6177940 

 And this was just one of many such attacks that collectively drained $2 million from the protocol.

 Adding insult to injury, Bedrock's response was slower than a sloth on sedatives.

 It took them over 2 hours to publicly acknowledge the exploit after Dedaub sounded the alarm, and nearly 4.5 hours to finally pause the vulnerable smart contracts.

 In the lightning-fast world of DeFi, that's an eternity - plenty of time for the digital horses to bolt, the stable to burn down, and the ashes to cool. 

 And in a twist that would make any security expert facepalm, this upgrade didn't undergo an audit. 

 In the world of DeFi, skipping an audit is like going skydiving and deciding parachutes are optional.

 It's a bold strategy, Cotton. Let's see if it pays off for 'em.

 The fallout was swift. As word spread faster than a viral meme, the DeFi community sprang into action.

 Pendle, holding a significant chunk of uniBTC, hit the brakes on their platform faster than you can say "not my bags." 

 Meanwhile, Bedrock's team, finally shaken from their slumber, scrambled to pause the vulnerable contracts. 

 But in crypto time, where fortunes are made and lost in the blink of an eye, their response felt like watching paint dry.

 The damage was done. Across eight chains - Ethereum, BNBChain, Arbitrum, Optimism, Mantle, Mode, BOB, and ZetaChain - the vulnerability left its mark.

 A total of 125 exploiters (because why let one person have all the fun?) had their field day. 

 In the end, Bedrock was left holding the bag, facing a $1.8 million hole in their liquidity and a whole lot of explaining to do.

 As they say in the crypto world: another day, another exploit.

 But this time, the price of skipping an audit came with a hefty price tag.

 If Bedrock itself can crumble so easily, what kind of foundation are we really building on? 

 And in the rush to mint the next big thing, are we creating bedrock or just burying landmines? 

 In the aftermath of Bedrock's $2 million face-palm moment, we're left shaking our heads in disbelief. 

 How does an unaudited upgrade slip through the cracks of a protocol handling millions? 

 Can they rebuild trust after this prehistoric-level security oversight?

 In the fast-paced world of DeFi, even the most solid foundations can shake.

 Bedrock's fumble serves as a stark reminder: in the rush to innovate, we might just be building castles on quicksand. 

 As we watch this saga unfold, one can't help but wonder: in the annals of crypto history, will Bedrock be remembered as a cornerstone, or just another stepping stone on the path to "doing better"? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
