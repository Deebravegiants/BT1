# [H] Velocore exploit: Velocore's high-speed Defi ambitions screech to a halt

## Summary
Severity: High
Target: Velocore
Loss: $6,800,000
Published: 06/02/2024
Source: https://rekt.news/velocore-rekt
Type: rekt-postmortem

## Details
## Velocore - Rekt

 Monday, June 3, 2024 Velocore - REKT 

 read this article also in : zh 

 Velocore's high-speed Defi ambitions screech to a halt. 

 The velo in Velocore proved too fast and furious, as the L2 DEX lost over $6.8 million in a devastating exploit on June 2nd across its pools on Linea and zkSync. 

 A vulnerability in Velocore's Balancer-style CPMM contract allowed an attacker to manipulate fee calculations, ultimately draining a sizable chunk of liquidity.

 The hack led the Linea team to halt block production, which has since resumed. 

 Velocore has offered a 10% bug bounty to the hacker, who has yet to respond.

 The actions by Linea’s team to halt the chain due to the exploit is posing Centralization concerns . 

 Despite undergoing multiple audits, Velocore's protocol still had an exploitable flaw.

 What's next for Velocore, a comeback or a permanent pit stop? 

 Credit: Officer CIA , Beosin , Linea , Velocore 
 The ever vigilant crypto gumshoe Officer CIA was the first to spot something fishy with Velocore’s liquidity pools. 

 According to the post-mortem from Velocore , the attacker sourced funds from Tornado Cash, bridged over to execute the dastardly exploit, and then deposited the ill-gotten gains back into Tornado Cash.

 The flurry of transactions started with the attacker directly invoking velocore__execute() to simulate huge withdrawals and jack up the feeMultiplier. With that jacked-up multiplier inflating effectiveFee1e9 past 100%, the villain executed a flash loan to scoop up most of the tokens and contract the pool.

 Finally, a small single-token withdrawal minted an egregiously large amount of liquidity tokens due to an underflow error, allowing the drainer to easily repay the flash loan and skip town with $6.8 million in ETH. 

 According to an analysis of the incident from Beosin , the LP Pool lacks permission verification. The attacker directly invoke the velocore__execute function (0xec378808) of the LP contract with a carefully constructed parameter to manipulate the feeMultiplier parameter of the contract.

 The value of feeMultiplier affects the number of tokens exchanged. The attacker then used the manipulated feeMultiplier parameter to call the execute function (0xd3115a8a) again through the router contract to drain funds from the LP pool.

 Attacker Address: 
 0x8cdc37ed79c5ef116b9dc2a53cb86acaca3716bf 

 Exploited Contracts: 

 0xed4e130f6f9e68918996f7e1e46a3306b3e12cec 

 0xb7f6354b2cfd3018b3261fbc63248a56a24ae91a 

 0xc030fba4b741b770f03e715c3a27d02c41fc9dae 

 0xf7f76b30a301524fe76508546B1e3762eF2B9267 

 Attack Transaction 1: 
 0xed11d5b013bf3296b1507da38b7bcb97845dd037d33d3d1b0c5e763889cdbed1 

 Attack Transaction 2: 
 0x37434e674efc4e7cfeed7746095301ace5636028906fe548b786ead286e35eb0 

 Attack Transaction 3: 
 0x4156d73cadc18419220f5bcf10deb4d97a3d3f7533d63ba90daeabc5fd11ba17 

 Final Fund Destination (Before Tornado Cash): 
 0xe4062fcade7ac0ed47ad794028967a2314ee02b3

 During the exploit, Linea team halted the sequencer to prevent additional funds bridging out, due to the inability to get in contact with Velocore. “This was the last resort action to protect users on Linea”, the network wrote on X . 

 While Linea stated its goal was to eventually take away the ability to halt the network from its team once significant decentralization had occurred, the protocol defended the decision to halt the chain.

 "Most L2s, including Linea, still rely on centralized technical operations which can be leveraged to protect ecosystem participants. Linea's core value is a permissionless, censorship-resistant environment so it was not a decision we took lightly," the network wrote .

 Velocore has initiated negotiations with its attacker to recover the $6.8 million in stolen ETH, they are offering 10% as a white hat bug bounty reward.

 According to official documents, Velocore claims to have undergone three rounds of audits , completed by Zokyo, Hacken and Scalebit in August of 2023. 

 With their pedal stuck to the metal on insecure code, Velocore has driven itself into a ditch, do they have enough horsepower left to get themselves out? 

 For a protocol that boasted multiple audits and solidified security, Velocore is now looking more like a rusty junker left for scrap after this $6.8 million drain. 

 While dangling a 10% bug bounty carrot, Velocore has yet to lure the hacker out from their Tornado Cash hideout.

 At this rate, the team may need to invest in psychic mediums to communicate with the drainer from the other side. 

 The question is whether this was an isolated crash, or just the first fender bender in a longer line of recurring collisions for Velocore.

 With so many blindspots somehow missed in their audit cycle, cautious crypto travelers may want to steer clear until this project gets completely overhauled from the chassis up. 

 Maybe Velocore finds a way to get their motors humming again or will this exploit force them to permanently park their DeFi dreams in the junker lot? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
