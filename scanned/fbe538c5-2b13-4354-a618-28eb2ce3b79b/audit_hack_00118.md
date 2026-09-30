# [M] Hacken exploit: When the security experts need security experts, you know something's gone horribly wrong

## Summary
Severity: Medium
Target: Hacken
Loss: $170,000
Published: 6/20/2025
Source: https://rekt.news/hacken-rekt
Type: rekt-postmortem

## Details
## Hacken - Rekt

 Tuesday, June 24, 2025 Hacken - Rekt - Bridge Key Compromise 

 read this article also in : 

 When the security experts need security experts, you know something's gone horribly wrong. 

 Hacken built its brand by securing DeFi from itself. But when it came to their own keys, the “smart contract cops” forgot to lock the door. 

 It all unraveled on June 20th, when a compromised private key opened the door to a $170K drain and a 99% collapse in token value.

 The irony cuts deeper than a smart contract vulnerability - this wasn't sophisticated code manipulation or a novel attack vector.

 Just human error during a bridge upgrade, exposing years of postponed security infrastructure that any auditor would flag as critical.

 While Hacken scrambles to rebrand this disaster as an architectural growing pain, the real takeaway smolders beneath the wreckage. 

 How can you trust a security firm that couldn't secure its own keys? 

 Credit: Peckshield , Cyvers , Hacken , Dyma Budorin , Twix , Coin Telegraph 
 First the alerts started pinging. 

 PeckShield caught the blood in the water on June 20th: "$HAI is hacked, resulting in price crash."

 Cyvers followed up with forensic clarity - confirming the attacker had seized minting privileges and unleashed 900 million $HAI tokens into circulation.

 The smoking gun? A bridge private key left exposed on a decommissioned DigitalOcean server - forgotten infrastructure with fatal consequences.

 Hacken killed the bridges , but the damage was done - tokens were already hemorrhaging across BSC and Ethereum. 

 Due to shallow liquidity pools , only ~$170K actually escaped before the bloodbath ended - though watching your token crater 99% hardly feels like getting off easy. 

 Meanwhile, CEO Dyma Budorin was pulling all-nighters trying to figure out what the hell happened.

 "We are online and making investigation," he posted at 3am , as the full picture was still coming together.

 His damage control tour continued with a mix of panic and defiance: "This accident pushed us to an action. We will merge into Hacken security token with all legal rights."

 Translation: We're going to spin this disaster into our master plan all along. 

 But first, Budorin had to admit the uncomfortable truth - it was a bridge private key compromise, calling it his "worst day" while promising that VeChain's solo-chain design would contain the fallout. 

 By June 21st, Hacken had workshopped their official response : this wasn't a hack, just "human error during architectural changes."

 Their post-incident report walked the damage control tightrope - the deployer wallet wasn't compromised , only the minter role keys were leaked, and they were totally planning to upgrade their bridge security anyway .

 The estimated loss: ~$170K , though that didn't account for the reputational damage of a security firm getting schooled by basic key management. 

 So how exactly do you turn 900 million phantom tokens into real money when everyone's watching? 

## The Mint and Dump

 Here’s what happens when unchecked minting power lands in the wrong hands. 

 The address behind it all didn’t bother hiding in the shadows. 

 Attacker Wallet on BSC: 
 0x2FA1789B009A05921eB64F10B8F0d30684661d2d 

 Attacker Wallet on Ethereum: 
 0x2FA1789B009A05921eB64F10B8F0d30684661d2d 

 The attack followed a brutally simple playbook - no complex smart contract gymnastics required.

 BSC Mint Transactions: 
 0xe8c895df8d99d3a680faf80bb65f80c53d8f2c48b5d48fe7c73883b6824aa30f 

 0x4836db1d5a038a616d99ae396d73129272123733e394a43ee99d019b26eb142f 

 0xd082fcfe41d20a42f979acea0b03c50c35c5dd97e61d3df8386a9463b13d7f58 

 Ethereum Mint Transaction: 
 0xa0b32ee67d572df80a10c439d395a9907492d6ef62cbf53be66b3145cf479ab6 

 Nine hundred million tokens conjured from thin air across both chains, then dumped faster than a hot potato. 

 When you can print money at will, why complicate things with DeFi wizardry? 

## Smart Money and Market Chaos

 While $HAI holders watched their portfolios evaporate, some traders found opportunity in the carnage. 

 Gate.io became an accidental arbitrage playground when their API leaked support for ETH network deposits - even though their UI hid it completely. 

 Sharp-eyed traders caught this discrepancy , stacked tokens from the compromised chains, and flipped them for profit on other exchanges before anyone could blink.

 Cross-chain deposit glitches turned into alpha for those quick enough to exploit the chaos.

 The token crashed 99% , then pulled off an 8x recovery pump - because apparently even disasters need hype cycles.

 Dip buyers who timed it right walked away with easy profits, while the rest learned an expensive lesson about liquidity traps.

 Meanwhile, $HAI somehow kept trading at multiples of its crash price across different venues - market efficiency was taking a coffee break. 

 But what happens when the attacker thinks they've gotten away clean? 

## The Plot Twist

 Three days later, Budorin dropped a bombshell on Twitter : "Thanks to Extractor, we were able to track all fund movements and timely block the account after his KuCoin deposit." 

 The hacker had made their first mistake - depositing funds on KuCoin , where real-world identity meets blockchain transactions. 

 Sometimes KYC can become Know Your Criminal.

 Suddenly "law enforcement in the process" wasn't just corporate posturing anymore .

 Meanwhile, Hacken's damage control strategy shifted into overdrive with promises that would make any marketing team proud.

 Transform $HAI into a regulated financial tool that merges token utility with equity rights? Check. 

 Merge with Hacken equity shareholders valued at over $100M? Double check. 

 Compensate legitimate holders through a future token swap ? Triple check with extra corporate buzzwords.

 The timing couldn't be more perfect - turn a massive security failure into the catalyst for their "always planned" tokenomics revolution.

 But here's the bitter irony that cuts deepest: Hacken's own Q1 2025 security report had warned that access control exploits were the number one threat to Web3, responsible for $1.6 billion in losses.

 "While smart contract vulnerabilities remain a threat, most damage is now caused by failures in people, processes, or permission systems," their report stated .

 They literally wrote the playbook on what not to do, then followed it to the letter. 

 When the security auditors can't audit themselves, who's left watching the watchers? 

 Hacken's $170K lesson proves that knowing about security and practicing it are two very different skills. 

 Five years of delayed multisig upgrades caught up with them in the worst possible way - 900 million minted tokens and a 99% price crater later. 

 While they spin this disaster into their grand tokenomics transformation, the damage to their credibility might be harder to fix than their bridge architecture.

 Smart traders turned the chaos into profit, law enforcement might get their man, and Hacken gets to learn that being your own worst case study isn't great for business.

 Hacken now promises to turn this embarrassment into a case study for others . Which is fitting - because the smartest lesson here came at their own expense.

 Their own security report warned that human error was DeFi's biggest threat - turns out they were writing their autobiography.

 The real question isn't whether Hacken can recover from this fumble, but whether anyone will trust a security firm that couldn't secure their own cookie jar. 

 In an industry built on trustless systems, what happens when the trust enforcers break their own rules? 
 
## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
