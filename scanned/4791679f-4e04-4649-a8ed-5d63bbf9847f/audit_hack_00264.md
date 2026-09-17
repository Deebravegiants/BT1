# [H] TesseraDao exploit: TesseraDAO's own manifesto warned investors about projects with centralized admin control , unrevoked permissions, and no independent audit

## Summary
Severity: High
Target: TesseraDao
Loss: $2,490,000
Published: 6/1/2026
Source: https://rekt.news/tesseradao-rekt
Type: rekt-postmortem

## Details
## TesseraDao - Rekt

 Tuesday, June 9, 2026 TesseraDao - Admin Privileges - Rekt 

 read this article also in : 

 The hollow protocol. Maybe not so much a project, but a performance with an exit plan. 

 Not a bug. Not an exploit. Just emptiness dressed as infrastructure. 

 TesseraDAO's own manifesto warned investors about projects with centralized admin control , unrevoked permissions, and no independent audit. It listed CertiK certification as proof of legitimacy .

 The CertiK audit was never completed . The admin rights were never revoked. The multi-sig governance promised on page one never existed.

 What did exist was a single private key with total authority over the entire protocol . Shape without form. Power without oversight. A god key in a hollow protocol.

 Nobody broke a single line of code. The code was perfect. The emptiness was the feature. 

 On June 1, 2026, whoever held it, or whoever took it, used every function it unlocked, reassigned roles, seized ownership, minted 99 million TSR tokens from nothing , dumped them for $2.49 million in stablecoins, and withdrew cleanly. 

 Shape without form, chain without colour. Paralyzed keys, gesture without motion.

 TSR collapsed 99% , before most holders knew anything had happened. 

 By the time the security community mapped the attack, 1,285.5 ETH was already cycling through Tornado Cash . 

 The attacker left no shadow. Six transactions, then gone.

 The architecture was straw, and it burned exactly as fast as straw burns.

 TesseraDAO said nothing. Not that day. Not the next. Not the day after that.

 Between the manifesto and the reality, between the promise and the drain, between the audit claimed and the audit never received, there was only silence. The team remained in shadow. 

 Three days after their treasury was emptied, the official account posted this : "Every protocol has a vision. What matters is the ability to execute it consistently." 

 Consistent execution. Shame the treasury wasn't part of the vision.

 The Telegram had voices. They were noise, bot accounts cycling through canned enthusiasm while the price collapsed: "structure feels unbreakable rn." 

 The structure had been broken three days prior.

 Now the holders are left in the twilight kingdom of a token at $0.0001343 , a Telegram full of bots , and a motivational quote from an account that has said nothing else since. 

 When a protocol publishes a manifesto about protecting investors, claims an audit it never received, and then loses everything through the exact vulnerability it promised to eliminate, was this ever really a protocol itself from the start, or did whoever held the key just disappear when it fell? 

 Credit: TesseraDAO , CertiK , QuillAudits , Specter , Peckshield , TesseraDao , TesseraDao Telegram , The Hollow Men by T.S. Eliot 
 Specter fired the first flare on June 2nd, roughly 19 hours after the exploit had already run its course. 

 "A project on BNB Chain, @TesseraDao, has been exploited. The attacker minted 99M $TSR and dumped the tokens for $2.4M. As a result, $TSR plunged 99%. The attacker has already deposited them into Tornado Cash."

 Clean, specific and damning. And almost a full day late, not through any fault of Specter's, but because the attack had been invisible.

 No alarm fired. No circuit breaker tripped. TSR's price chart was the only signal , sunlight on a broken glass, and by the time anyone was reading it, the money was already gone.

 Three security firms watched with direct eyes. The team did not watch at all. 

 Between Specter's alert and PeckShield's confirmation , the money kept moving. 

 PeckShield added the cross-chain detail Specter hadn't yet captured , the exploiter had bridged the stolen funds to Ethereum and was already running 1,285.5 ETH through Tornado Cash . The trail grew cold. The shadow grew longer.

 Between PeckShield and QuillAudits , the trail cooled further.

 Between all three firms and any acknowledgment from TesseraDAO, there was nothing. Just silence. Just shadow.

 Two and a half hours after Specter, QuillAudits published the transaction-level breakdown nobody else had bothered to produce, transactions linked, function calls named , addresses dropped . 

 QuillAudits put it plainly : The attacker didn't find a bug in the code. They got the keys and used the protocol's own functions against it. 

 The architecture was straw, and QuillAudits had just documented exactly how it burned.

 Then QuillAudits flagged something that should have set off a second alarm , the compromised admin address wasn't just a historical artifact. It was still live, actively transferring ownership of other TesseraDAO-related contracts.

 Shape without form, gesture without motion.

 The initial drain was done. The cleanup wasn't. 

 Three security firms spoke. One team remained silent. 

 Specter noted something else worth sitting with , the UXLINK exploiter, responsible for a $41 million drain in September 2025 , was simultaneously running funds through Tornado Cash alongside the TesseraDAO attacker.

 Roughly $7.1M in UXLINK proceeds moving through the mixer in parallel.

 Two separate exploits, one mixer, one window. Nobody at TesseraDAO was watching, because maybe there was nobody at TesseraDAO to watch. 

 The voices were empty. Because there was no one to hear them. 

 June 1st brought the drain. June 2nd brought Specter's alert . June 4th brought a motivational quote from the team that was exploited. With no acknowledgement in between.

 Between the idea and the reality, between the motion and the act - the treasury fell.

 When the security community fully documents your exploit before you've even noticed it happened, what does that tell your users about who was actually watching the protocol? 

 Were the hollow men watching? Or had they already left? 

## God Key

 TesseraDAO wasn't hacked. 

 It was administered by someone who had no business holding the keys. 

 Their own manifesto called it out directly.

 Under "Decentralized Security," question four : "Are contract admin rights permanently revoked?”

 Their answer : “Destroying admin rights ensures perpetual, autonomous operation.”

 They left out the part where the admin rights were never destroyed . They were never revoked. Someone held them until the very end. 

 Under "Decentralized Security," question five : "Are all on-chain contracts security audited?

 Their answer : Certified by CertiK, the highest standard of security and transparency."

 The admin rights were never revoked. There was no multi-sig. The CertiK audit was never completed .

 Under "Decentralized Security," question six : "Does the entire system use multi-sig governance?”

 Their answer : “10-party multi-sig ensures checks, balance, and enhanced security.” 

 They left out the part where there was no multi-sig . No 10 parties, no checks, no balance. Just one key, and whoever held it. 

 Every question they asked of other protocols, they failed themselves. The manifesto was straw . The architecture beneath it was straw. One key, holding everything up.

 That key controlled minting, role assignment, ownership transfer, trading, and withdrawal simultaneously, no delay, no second signature, no circuit breaker between the command and execution. Whatever it said, the protocol did.

 That's hollow authority. All power, no oversight.

 The attacker didn't need to be clever. They only needed one thing. 

 QuillAudits mapped every step . One key, every function wide open. This is how a hollow protocol empties. 

 Using admin access, the attacker reassigned the trader and withdrawer roles to their own wallet: 
 0xa748067f218fd63b6dd69b7744cdac4bc41644aa6b8cadcb8a6daff74e79d721 

 transferOwnership() handed them the entire protocol outright, one transaction, no quorum: 
 0xf799e7b0cdbccf843b2f13768a681c2e07479c8cf1c58452378bbbc2af7d2453 

 99 million TSR materialized from the zero address : 

 0x25093e573c116562c8839dc67a15ac21761271006a8dfe50b18fa475564bfcd1 

 trade() converted those tokens into real money using the protocol's own swap function: 
 0x756d33e7a0f8f0e54e321d1a0a3fda334896552ab44a9dac7b55dd899d88c9bb 

 2,475,659 BSC-USD walked out cleanly to the attacker wallet : 

 0xc2313c9fdb800f9c66171f12e81f83e47a40c91129fce6c40bbc5e969e5cf134 

 Every function that was controlled by one key, with no oversight and total control. 

 The admin key cast a long shadow, it controlled everything, including the exploit. 

 The keys were paralyzed. The gesture was without motion. The protocol obeyed.

 Between the manifesto and the architecture, between the promise and the key , between the governance claimed and the governance never delivered, there was only the admin. And it fell.

 No code was broken. Only trust was.

 No audit that appears to have been completed. No multi-sig was deployed. No rights were revoked. No team was even visible.

 When you hand one key the power to do everything and call it decentralized, what exactly are you building? A protocol, or an exit waiting for the right moment? 

 Or were you just building a hollow protocol from the start? 

## Clean Exit

 The attacker didn't linger. Once the architecture had done its job, the money moved in one direction. The doors were all open. Nobody was watching. All that remained was to walk through them. 

 Between the idea and the reality, between the motion and the act, the keys fell. 

 Admin Role Hijacked: 
 0xa748067f218fd63b6dd69b7744cdac4bc41644aa6b8cadcb8a6daff74e79d721 

 Ownership Transferred: 
 0xf799e7b0cdbccf843b2f13768a681c2e07479c8cf1c58452378bbbc2af7d2453 

 Then came the drain.

 Attacker Wallet: 
 0x2201037a1755ec48ec5f00fea21a10a9e56f2dd8 

 Victim Contract: 
 0x6f2b45b950d1739ef67c76f4106df6d6e84904cb 

 TSR Token: 
 0x2f8a0cc5fe14c0cf7f7f95058e6410bae0061fcf 

 Compromised Admin Role: 
 0x61a23e0eba09096ffeb954aa8a93c3079e87cf17 

 99,000,000 TSR minted from the null address directly into the victim contract. Zero cost. Zero backing. Tokens manufactured from nothing, using a power the protocol had left completely unguarded, the hollow minting function of an empty protocol. 

 Mint Transaction: 0x25093e573c116562c8839dc67a15ac21761271006a8dfe50b18fa475564bfcd1 

 The trade() function executed. 99 million TSR out, $2,475,659.06 in BSC-USD back in. The sudden flood of supply did exactly what it was designed to do, collapse the price.

 TSR went from $5.50 to $0.0002 in minutes.

 Between the mint and the dump, the treasury vanished. Holders watching their portfolios had no idea what they were looking at. Not silence. Not shadow. Just a chart collapsing in real-time.

 Trade Transaction: 0x756d33e7a0f8f0e54e321d1a0a3fda334896552ab44a9dac7b55dd899d88c9bb 

 The first withdrawal. $2,475,659.06 pulled cleanly from the contract to the attacker wallet. No resistance. No delay. The withdrawer role they had reassigned twenty minutes earlier worked exactly as intended. The door had been left open. Someone walked through it. Shape without form. The protocol emptied. 

 Withdrawal Transaction 1: 0xc2313c9fdb800f9c66171f12e81f83e47a40c91129fce6c40bbc5e969e5cf134 

 They came back for the loose change. A final sweep of $16,224 BSC-USD, the last meaningful balance sitting in the contract. They took that too.

 Withdrawal Transaction 2: 0x1d3b28b494687fa9677c6cb07719ebe1ea2ae9a9dbc5924565a491699d7ff988 

 What remained in the exploited contract : Fifty cents.

 $2.49 million gone. One protocol evaporated. 

 From there, the exit was methodical, stablecoin proceeds bridged from BNB Chain to Ethereum, then 1,285.5 ETH moved through Tornado Cash in fractional deposits, each one anonymous, each one permanent, each one a door closing behind whoever was walking out. The attacker left no shadow. 

 PeckShield confirmed the Tornado Cash laundering route . What went in doesn't come out with a name attached. Just the echo of a protocol that was hollow from the start.

 Recovery Outlook: Zero.

 The victim contract showed normal trade activity roughly 40 days before the attack, small trades, routine, unremarkable. Then an almost 40-day gap. Then everything was taken. The straw had turned to dust long before anyone struck a match. That gap doesn't prove anything. But it does raise a question about who knew what, and when.

 Between the vision and the reality, between the token and Tornado Cash, the admin key fell. For Thine is the Wallet.

 When an attacker returns for the last $16k after already clearing $2.49 million, what does that tell you about how carefully this was planned, and how well they knew every dollar that was sitting there?

 Were they watching while the empty shell held itself together? 

 Or were they the ones holding it? 

## The Hollow Protocol

 We are the hollow devs. We are the stuffed wallets. Leaning together. Whitepaper filled with straw. 

 TesseraDAO had one contact channel . Not an email. Not a support desk. Not a single named team member anywhere on the internet. A Telegram group . That was the door. The only door. 

 On June 4th, three days after $2.49 million left the contract and 1,285.5 ETH dissolved into Tornado Cash, Rekt News walked through it and asked the question nobody from the project had bothered to answer.

 Rekt.news : “Curious when you guys are going to let people know that you have been exploited?“

 What came back wasn't silence. Silence would have been honest. 

 Alas! Our dried voices, when we post, are quiet and meaningless, as bots in a Telegram. 

 Within two minutes, five accounts flooded the chat with canned enthusiasm: " huge upside if team delivers ," " holders will love compounding ," " mainnet launch when? "

 Rosendo, Isabel, Brennon Schinner, Gennaro Jacobson, Estevan Wiza, Amari - the same names cycling through the same chat for hours, performing on cue.

 Not a community. Wallpaper. The question was buried and the script kept running.

 Brennon Schinner : “TSR chart looks like a staircase.”

 Gennaro Jacobson : “TSR becoming a safe zone token.”

 Amari : “structure tighter than most blue chips.”

 Amari : “structure feels unbreakable rn.”

 They were either clearly tone deaf to the situation or Rekt News stepped into a portal to another dimension. 

 The chart was at $0.0002 at the time . The structure had been broken three days prior. The treasury held fifty cents. Not one voice mentioned the exploit. Not one asked why TSR had collapsed 99%. 

 Not one wondered where the team was. Shape without form, chain without colour, Paralyzed keys, gesture without motion.

 Then this, buried nearly an hour after Rekt News had asked the only question that mattered:

 Amari : “all permissions burned = big respect.”

 The permissions weren't burned. They were stolen. Whoever held them had already bridged the proceeds to Ethereum and cycled 1,285.5 ETH through Tornado Cash. 

 But in this Telegram, in this Potemkin village of a protocol, the performance never broke character. 

 Isabel : “omg tomorrow is final AMA.”

 There was no AMA. There was no tomorrow for this protocol. There was no team left to host one.

 There is no team here, in this hollow protocol, this broken jaw of our lost treasury.

 A script running on a loop while the only real question sat unanswered, sinking further from view with every new message.

 Isabel : “tessera devs deserve respect.”

 Sightless, unless the devs appear, as the perpetual promise, multifoliate roadmap of the holders' twilight kingdom. 

 No dev appeared. No mod stepped in. No team member surfaced to acknowledge what three security firms had documented in full, publicly, for three days straight. Just the voices, cycling on repeat. 

 Filling the silence with noise that sounded, from a distance, like a living protocol.

 Between the vision and the reality, between the roadmap and the act, falls the Admin Key.

 Between the mint and the dump, between the token and Tornado Cash, falls the Admin Key. For Thine is the Wallet.

 And then, as if to close the loop, the official TesseraDao’s Twitter account finally posted .

 Not an acknowledgment. Not a plan. Not a word about the exploit that had emptied everything while nobody watched : "Every protocol has a vision. What matters is the ability to execute it consistently."

 This is the way the treasury ends. Not with a bang but a motivational quote. 

 When the bots outlast the builders and the vision statement outlasts the treasury, was T.S. Eliot writing about hollow men , or was he writing an early whitepaper for what DeFi would become? 

 TesseraDAO didn't collapse. It evaporated. 

 No team came forward. No postmortem was published. No bounty was offered. No compensation plan floated. They did not even acknowledge that they were exploited. 

 $2.49 million gone, 1,285.5 ETH through Tornado Cash , all of fifty cents left in the contract . The treasury didn't just get emptied, it got swept.

 Every structural choice TesseraDAO made pointed in the same direction: One key with total authority, no audit that appears to have been completed, no multisig, no timelock, no named team, no way to reach anyone, and a community that turned out to be wallpaper.

 Whether the key was stolen or handed over has never been answered, and at this point, may never be.

 Between the theft and the handover, between the victim and the villain, there was only silence. 

 Are they actually trying to recover the funds? Did they get hacked themselves, or did they Run Under Ground? 

 Holders are left in the twilight kingdom of a token that lost 99% of its value, a Telegram full of bots , and an account that has posted twice more since the drain, neither time to acknowledge it.

 On June 6th : "Innovation is not about adding complexity. It's about creating systems that remain effective as they scale. That is the principle TSR continues to build around."

 The system was effective. It drained at scale.

 Then on June 6th again : "Every protocol has a vision. What matters is the ability to execute it consistently. TESSERA is committed to turning structure into action and ideas into on-chain reality."

 Consistency builds trust. The treasury is gone. The trust went with it. 

 When a protocol is built so that one person can take everything in a few transactions, disappear without a word, and leave behind only a vision statement, was it ever really a protocol at all, or just a very elaborate goodbye? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
