# [C] ByBit exploit: Sophisticated hackers orchestrated a precision strike on the exchange, siphoning away 401,346 ETH ($1.11B), 90,375 stETH ($250.8M), 15,000 cmETH ($44M

## Summary
Severity: Critical
Target: ByBit
Loss: $1,436,173,027
Published: 2/21/2025
Source: https://rekt.news/bybit-rekt
Type: rekt-postmortem

## Details
## ByBit - Rekt

 Saturday, February 22, 2025 ByBit - Rekt - Lazarus 

 read this article also in : 

 $1.43 billion gone! The most financially devastating attack in crypto history just rewrote the record books and took the top spot on the Rekt Leaderboard . 

 Sophisticated hackers orchestrated a precision strike on the exchange, siphoning away 401,346 ETH ($1.11B), 90,375 stETH ($250.8M), 15,000 cmETH ($44M) and 8,000 mETH ($23.5M) in a matter of minutes. 

 The attackers executed a familiar front-end spoofing attack, deceiving multisig signers into authorizing what they believed were legitimate transactions.

 ByBit could only watch as these colossal funds disappeared into a labyrinth of 40+ wallet addresses.

 This theft more than doubles the previous record holder on the infamous Rekt Leaderboard, leaving competitors in its wake.

 Another exchange, another compromised multisig, another team got gamed. 

 Haven’t we heard this one before? 

 Credit: ZachXBT , SlowMist , Peckshield , ByBit , Ben Zhou , Metasleuth , BitMEX , Nanak Nihal , Derek Silva , Meir Dolev , Adam Cochran , Arkham Intel , Tayvano , SEAL , Abbas Khan , Vladimir S , Chainflip 
 First reported by ZachXBT in his Telegram on Friday, "Currently monitoring suspicious outflows from Bybit." 

 Within minutes, blockchain security firms including SlowMist and Peckshield confirmed the worst – ByBit was bleeding funds at an unprecedented rate.

 The damage was done before ByBit could even blink.

 It wasn't long before the exchange confirmed the hack , but by then, the funds had vanished into the ether.

 The hack unfolded with lightning speed, draining ByBit’s Ethereum cold wallet while signers remained blissfully unaware of the true transactions they were authorizing.

 All they saw were legitimate-looking interfaces, masking the catastrophic theft happening underneath.

 Ben Zhou, co-founder and CEO of ByBit, confirmed what many feared - this wasn't a simple key compromise but something far more insidious. 

 "It appears that this specific transaction was masked, all the signers saw the masked UI which showed the correct address and the URL was from Safe." 

 XJ from Peckshield revealed the surgical precision of the attack.

 The hackers deployed a sophisticated bait-and-switch.

 They created a transaction that appeared to be a routine cold-to-hot wallet transfer.

 What signers actually approved was a wallet implementation upgrade containing malicious code. 

 The unverified implementation included a hidden "sweepERC20()" function. 

 Once deployed, this function gave the attackers complete control to drain the wallet at will.

 This wasn't just a smash and grab - the attackers had orchestrated a meticulous plan with the precision of a military operation and the timing of a championship chess player.

 This address would soon gain infamy as the command center for the largest theft in crypto history: 
 0x47666Fab8bd0Ac7003bce3f5C3585383F09486E2 

 Compromised Bybit Cold Wallet: 
 0x1Db92e2EeBC8E0c075a02BeA49a2935BcD2dFCF4 

 The fatal moment came when the attacker called the Sweep Function on ByBit's hot wallet, triggering this transaction that moved 401,346.76 ETH in a single devastating swoop:

 Attack Transaction: 
 0xb61413c495fdad6114a7aa863a00b2e3c28945979a10885b12b30316ea9f072c 

 After pulling off the heist, the attackers launched a full-blown operation to scatter the stolen funds across the blockchain.

 ZachXBT tracked as they split 10,000 ETH across 39 addresses, then another 10,000 ETH to 9 more addresses - a blockchain shell game designed to outpace tracking efforts. 

 If you want to track the stolen funds: 

 Stolen funds tracked by Metasleuth 

 ByBit Hacker on Arkham 

## Crisis Management in Real-Time

 To ByBit's credit, they moved quickly to address the disaster. 

 Shortly after the attack, Ben Zhou took to Twitter to announce that, "Bybit is Solvent even if this hack loss is not recovered, all of clients assets are 1 to 1 backed, we can cover the loss." 

 He followed up with a livestream and drove home some key points in an attempt to contain the damage:

- 
 Only the Ethereum cold wallet was affected.

- 
 All user funds are safe.

- 
 ByBit Treasury has enough funds to cover the full loss.

- 
 They're securing a bridge loan from partners (80% committed at the time of the announcement).

- 
 Withdrawals remain active, albeit slowed.

 Almost a rarity in crisis communications and in a timely fashion on a Friday evening.

 According to BitMEX Research, roughly 75% of ByBit's ETH user deposits were stolen in the attack.

 Their quick back-of-envelope calculation based on ByBit's published reserve ratios suggested the exchange remains solvent despite the gargantuan loss. 

 What's the real cost of 'trust us, we're good for it' in an industry built to eliminate the need for trust in the first place? 

## Blind Faith in Blind Signing

 The ByBit hack highlights a fundamental vulnerability plaguing even the most sophisticated crypto operations. 

 As Nanak Nihal explained , "There is a name for this and it's BLIND SIGNING. Please please please stop using hardware wallets and multisigs and thinking you are safe." 

 The fatal flaw? Even with hardware wallets and multi-signature requirements, signers still trust their device's interface to accurately represent what they're approving.

 Once that interface is compromised, all security measures collapse like a house of cards.

 Derek Silva put it bluntly , "So, in essence, a group of ByBit executives, who should have significant OpSec training, blindly signed a transaction without asking any of the other multi-sig owners to confirm what it was for." 

 How many times does this have to happen before we admit that ‘sophisticated security’ isn’t enough when the same attack keeps slipping through the cracks? 

## Stop Me If You Heard This One Before

 Meir Dolev, Founder/CTO of Cyvers, identified something even more chilling - the attackers had conducted several dry runs two days prior to the attack. 

 Like professional bank robbers casing the joint, they had thoroughly tested their approach, ensuring everything would work flawlessly when the time came. 

 This wasn't their first rodeo. Security researcher Tayvano pointed out the devastating pattern ,

 “They’ve done this 5 times now. Please start taking it seriously.”

 The attack methodology mirrors recent high-profile hacks , such as those against WazirX , Radiant Capital , and DMM Bitcoin .

 In these incidents , funds were stolen directly from the organizations’ multisig wallets, but crucially, the private keys themselves were not compromised.

 The keys backing the multisig were held on hardware wallets, controlled by distinct parties within each organization. 

 As Adam Cochran observed , "Only two ways to do that would be a shotgun approach of targeting every senior person who works at ByBit until you get the signers, or a malware in network that attaches to internal docs until normal operations have spread to everyone needed." 

 This points to a much deeper compromise than simple UI spoofing.

 The attackers may have had persistent access to ByBit's internal systems, monitoring operations and communications until the perfect moment arrived.

 The most disturbing aspect? The attack succeeded because as soon as Ben Zhou signed, the attackers immediately executed the transaction themselves - not waiting for ByBit's systems to process it normally. 

 And just hours after the hack, ZachXBT cracked the case wide open , solving Arkham Intel's bounty by linking the attack to the LAZARUS GROUP, North Korea's infamous state-sponsored hacking organization.

 ZachXBT's submission was a masterpiece - analyzing test transactions, connected wallets, and timing analyses, and solving the bounty in a blistering four hours.

 And to make matters worse, it's a repeat offender backed by a nation-state. 

 Will this $1.43 billion heist be the wake-up call our industry desperately needs? 

## The Writing Has Been On The Wall

 The security community has been screaming about these vulnerabilities for months. 

 Tayvano's comprehensive thread on the attack pattern pointed to a simple but effective solution: 

 "Your best bet is to not allow them to get your device. That means hardware wallets. But it also means not using your daily computer when signing txns with that hardware wallet. Get an alt device for signing... It's dead simple."

 Other recommendations from Nanak Nihal : 

- 
 Use dedicated devices solely for transaction signing.

- 
 Keep these devices offline except when needed.

- 
 Consider secure operating systems like Qubes .

- 
 Use sandboxed environments when signing transactions.

- 
 Implement proper verification systems between signers.

 Vladimir S. outlined specific tools that exchanges should implement after this hack, including: 

- 
 End-to-end encryption for all communications.

- 
 Hardware security modules (HSMs) for key storage.

- 
 Custom signing verification apps to double-check transaction details.

- 
 Physical security keys with biometric verification.

- 
 Network segregation for all signing operations.

 As one commenter noted with devastating simplicity, "Having a separate laptop will get you 99.99% of the way there. Refurbished MacBook Pro, costs $900/pop”.

 A basement bargain compared to $1.43 billion. The brutal arithmetic speaks for itself.

 For the price of just one luxury watch or a high-end exec dinner, ByBit could have purchased dedicated signing devices for every multisig participant and still had change left for security training. 

 When the solution costs less than 0.0001% of what was stolen, what's the real reason these hacks keep happening? 

## The North Korean Trojan Horse

 SEAL's advisory on the DPRK threat pulls no punches. TraderTraitor (Lazarus Group's alias) begins their attacks with sophisticated social engineering, creating fake recruiter personas and reaching out over LinkedIn, Telegram, or Twitter. 

 They spend months performing reconnaissance, deploying malware like malicious Chrome extensions to modify trusted websites. 

 The Lazarus Group's playbook is ruthlessly efficient.

 They first find targeted employees through social engineering, add private GitHub repository access to the victims through live chat tools, and trick users into running code containing backdoors.

 How many more billion-dollar exchanges need to fall for social engineering before the industry admits it has an OpSec problem? 

## A $140 Million Hail Mary

 ByBit has launched a $140 million recovery bounty program - approximately 10% of the stolen funds - to "hunt for the perpetrators of crypto's largest heist in history." 

 An impressive figure, until you realize they're hunting a state-sponsored group that just pulled off a billion-dollar heist. 

 And the Lazarus Group isn't waiting around - they've already started moving the funds .

 The next day, they transferred 5,000 ETH to a new address and began laundering it through eXch (a centralized mixer) while bridging funds to Bitcoin via Chainflip .

 Some platforms like Tether managed to freeze 181,000 USDT , but it's a drop in the ocean of stolen assets.

 A review of bug bounty programs across major exchanges reveals an uncomfortable truth: most treat security as an afterthought. 

 While Kraken and Coinbase offer bounties up to $1 million, others like Bitget cap their rewards at a measly $3,000. 

 For platforms handling billions in user funds, these numbers are laughably inadequate.

 But the security theater doesn't stop there. In an industry literally built on cryptography and security, having a Chief Security Officer is somehow still optional.

 While Kraken , Binance , and Coinbase recognize the need for C-level security leadership, others like ByBit are content to outsource their security to third parties . 

 Because why have dedicated security leadership when you can just pay ransoms and bounties after the fact? 

 $1.43 billion vanished - more than double the previous record holder Ronin Network's $624 million heist. 

 ByBit's catastrophe has rewritten the crypto disaster leaderboard, making all previous thefts look like pocket change. 

 This wasn’t just any hack, this was a hack on steroids.

 Tayvano wants to know if they can take the rest of the year off now?

 Five exchanges have now fallen to the same attack vector, all while believing their hardware wallets and multisigs made them invincible.

 As Tayvano brutally summarized it the best…

 "The pixels that you see on your screen always come from somewhere else. If a threat actor compromises your computer, they can make the pixels display whatever they want. What you see will NOT be an accurate representation of what's actually happening behind the scenes. And you will not know until it's too late." 

 The North Korean playbook is now crystal clear: compromise devices, mask interfaces, and wait patiently for the perfect moment.

 The Lazarus Group isn't just hacking exchanges; they're exploiting the fundamental assumptions of digital trust.

 While exchanges scramble for stopgap solutions, North Korea's hackers likely already have their crosshairs trained on the next billion-dollar payday. 

 When we can't trust what we see on our own screens, what happens when the next target is your exchange, your wallet, your assets? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
