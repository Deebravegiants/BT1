# [M] SIR Trading exploit: SIR Trading just had its entire $355K TVL vanish after a hacker turned Ethereum's shiny new transient storage feature into a weapon of mass destructio

## Summary
Severity: Medium
Target: SIR Trading
Loss: $355,000
Published: 3/30/2025
Source: https://rekt.news/sirtrading-rekt
Type: rekt-postmortem

## Details
## SIR Trading - Rekt

 Tuesday, April 1, 2025 SIR Trading - Rekt 

 read this article also in : 

 SIR Trading just had its entire $355K TVL vanish after a hacker turned Ethereum's shiny new transient storage feature into a weapon of mass destruction. 

 While the founder was posting an odd story about North Korean devs getting "liquidated" on video calls, someone else was busy liquidating SIR Trading for real. 

 The attacker crafted a vanity address and calculated the precise mint amount needed to bypass security checks in the protocol's uniswapV3SwapCallback function.

 The hacker struck, leaving the protocol’s vault emptier than VCs' promises.

 Four years of late-night coding and $70K raised from Twitter believers evaporated faster than gas fees on an NFT drop.

 The founder’s response? A desperate plea, offering the attacker $100K to return the remaining funds - the DeFi equivalent of leaving a "pretty please" note after a bank robbery.

 One security audit clearly wasn’t enough to spot the fatal collision lurking in Ethereum’s newest storage slots. 

 Who knew that implementing bleeding-edge Ethereum features without understanding their security implications would end badly? 

 Credit: SIR Trading , TenArmorAlert , Decurity , Xatarrer , SupLabsYi , SlowMist 
 SIR Trading (Synthetics Implemented Right) lost its entire $355K TVL on March 30th to an attacker who exploited a vulnerability in the protocol's transient storage implementation. 

 The protocol, which only launched on February 20th , managed to last just over a month before meeting its demise. So much for "Implemented Right."

 SIR Trading broke the bad news themselves : "SIR has been hacked, do not deposit any further funds. We will post more asap."

 TenArmor Security quickly confirmed the attack , tracking the stolen funds to Railgun.

 They identified the root cause : a transient storage collision in the uniswapV3SwapCallback function, where slot 1 was used for both the Uniswap pool address and the minted token amount. 

 Decurity described it as a "clever attack" targeting the Vault contract. The callback function was playing security guard, checking IDs at the door by making sure the transient storage slot 0x1 matched the caller's address. 

 One fatal problem - the same bouncer storing his grocery list in the guest book.

 The function dumped the variable "amount" into the exact same memory slot it was using for verification.

 So how did the attacker transform this digital slip-up into a $355K payday? 

 Security researcher SuplabsYi laid out some of the details. 

 The first step? Brute-force a vanity address that, when read as a number, matched a very specific 29-digit value: 95759995883742311247042417521410689.

 No big deal - just conjure up a wallet address that perfectly equals this number when converted.

 Ethereum treats addresses as 160-bit numbers, derived from the last 20 bytes of the Keccak-256 hash of a public key, as documented in the Ethereum specification .

 The attacker needed to brute-force one that, when converted, precisely equaled this value - turning a random string into a precision-crafted exploit key.

 With enough computational power and the right tools (like VanityEth or GPU-based brute-forcing ), this was difficult but not impossible. 

 Casual afternoon math problem. 

 With vanity address in hand, the attacker unleashed their master plan - no random smash-and-grab, just one hell of a surgical strike.

 SlowMist broke down how the hacker turned Ethereum's shiny new TSTORE and TLOAD opcodes into weapons of mass destruction.

 Cook up some malicious tokens and a UniswapV3 pool - basic ingredients for any respectable DeFi disaster.

 Initialize a leverage market in the Vault contract, laying breadcrumbs for the protocol to follow right into the trap. 

 When the mint function ran, the protocol obediently used TSTORE to save the UniswapV3 pool address in slot 0x1 of transient storage - just as the developers intended. 

 The fatal flaw? Later in that same function, it mindlessly overwrote that slot with the attacker's precision-crafted mint amount: 95759995883742311247042417521410689.

 With the storage poisoned, the attacker deployed their attack contract using CREATE2, ensuring its address matched their calculated value down to the last byte.

 The final stroke? Call uniswapV3SwapCallback directly. 

 When the function checked TLOAD(slot 0x1) to verify the caller, it found the attacker's address instead of the legitimate pool - digital identity theft complete. 

 Like showing up at the bank with someone else's ID and walking out with their life savings.

 Game. Set. Match.

 The Vault never stood a chance. The attacker kept spamming uniswapV3SwapCallback from their malicious contract, siphoning funds with every call. 

 Then, like any seasoned pro, they washed the loot through Railgun - one of crypto’s favorite laundromat for post-exploit dry cleaning. 

 Attacker’s Address: 
 0x27defcfa6498f957918f407ed8a58eba2884768c 

 Vulnerable Contract Address: 
 0xb91ae2c8365fd45030aba84a4666c4db074e53e7 

 Attack Transaction: 
 0xa05f047ddfdad9126624c4496b5d4a59f961ee7c091e7b4e38cee86f1335736f 

## The Aftermath

 The universe has a twisted sense of humor. 

 Just a day before the exploit, SIR Trading’s founder, Xatarrer, posted a bizarre story on Twitter - one that, in hindsight, makes the timing of the attack feel a little too coincidental. 

 He claimed that a prospective dev had reached out to work for SIR. A promising candidate, well-connected, with top-tier references.

 But before hiring, Xatarrer decided to subject him to the Kim Jong Un test - his personal method of weeding out North Korean operatives.

 The “test” was simple, say something along the line of: 

 “Kim Jong Un is a fat ass ugly soyman.” 

 According to Xatarrer, the dev hesitated, his video feed blurred, and then—

 “BANG! The fake background had unblurred a bit, and I saw him lying on the floor with blood around. He had been fucking liquidated.”

 Before disappearing, the alleged dev typed one last cryptic message: 

 "RPC sync issues affected my internal organs. While liquidation occurred at a remarkable 95% LTV - highest on North Korea - I recognize I fell short by my expectation." 

 The alleged dev’s Alias on Twitter is xPOSITION .

 Hours later, SIR Trading itself was liquidated - less violently, but far more expensively.

 When reality hit, Xatarrer’s tone shifted from shitposting to sheer devastation: 

 “Sorry. This is devastating news. I just came back asap from my kid’s training. I am in shock. Sorry to everyone. Investors, believers… I poured 4 years of my life. And now we just lost most of the funds to an attacker. I have no words.” 

 Shock quickly turned to negotiation. SIR Trading’s team sent a message to the attacker that reads like a LinkedIn sob story with a bounty attached:

 “If you want to discuss privately… SIR isn’t some VC-backed copy-paste DeFi project, but a completely new type of leverage primitive. It’s four years of late-night coding, $70k from friends and believers, and we grew to $400k TVL organically without any advertising. If you keep 100% of the funds, there is no chance for us to survive. Here is my proposal: keep $100k as a fair share for your critical bug find, and return the remaining… We’ll call it even. No legal games, no drama.”

 Translation: “We couldn’t afford more than one audit, so please be a good sport and only take 28% of our TVL.” 

 And yes, one audit was all they had. 

 Egis Security reviewed SIR Trading back in February, managing to find a few high-severity issues.

 A single audit for a protocol implementing Ethereum’s newest and least-tested storage feature?

 That’s like bringing a water pistol to a flamethrower fight.

 Xatarrer admitted as much: “We raised around $70k from folks in here which allowed us to do 1 audit which unfortunately wasn’t enough.” 

 The founder's desperation was palpable: “We have walked alone because I have been basically stonewalled by VCs. Not even getting any feedback. Not sure how we would relaunch from here, but if you have any idea I’m all ears.” 

 No word yet on whether the hacker plans to accept the $100K bounty offer, but history suggests they’ll either take everything or return nothing. DeFi’s hostage negotiations rarely end in compromise.

 The SIR team now says they've lost "most of their cash" but are ready for relaunch . They're desperately searching for auditors, offering token equity (no cash) to anyone willing to review their code.

 Their pitch? "The risk is limited as we already showed the product can work live and the potential is huge." And no, this isn't an April Fools joke. 

 The product worked - until it didn't. Like a car with faulty brakes, it ran fine right up until the crash. 

 The team says "risk is limited" after losing their entire TVL, while asking auditors to work for IOUs instead of actual money.

 But if you are a firm believer in doubling down on stupid, SIR Trading's relaunch might be just the opportunity you've been waiting for.

 The exploit has raised urgent questions about Ethereum’s transient storage feature - Dencun’s shiny new upgrade may have just claimed its first victim .

 As SupLabsYi put it : “This may be one of the first real-world attacks exploiting its vulnerabilities.” 

 "In DeFi's never-ending race to implement shiny new features, are users just the crash test dummies? 

 Ethereum handed developers a shiny new storage tool, and SIR Trading might’ve just been the first to misuse it. 

 Transient storage was marketed as a more gas-efficient solution, not a potential backdoor for hackers to waltz right in. 

 But here we are, with an attacker who didn’t simply exploit a coding flaw - they turned a bit of math into a master key, brute-forcing a vanity address that unlocked SIR Trading’s vault like it was theirs for the taking.

 As SIR Trading scrambles to negotiate with their digital kidnapper, the rest of DeFi should be taking notes: when integrating Ethereum’s latest innovations, maybe don’t cut corners on security with just a $70K budget.

 The real tragedy here isn’t that SIR Trading got exploited - it’s that the next protocol to mishandle transient storage could have a much bigger target on its back than $355K.

 When your entire security model is built around keeping values separate in shared memory, you’re not just "innovating" - you’re one exploit away from insolvency. 

 With new features like transient storage, innovation is a double-edged sword - how many more protocols need to fall before the community learns that cutting-edge doesn’t always mean safe? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
