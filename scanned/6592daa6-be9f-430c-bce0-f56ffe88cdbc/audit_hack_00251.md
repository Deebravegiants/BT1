# [C] Step Finance exploit: Ninety minutes and one compromised laptop separated Step Finance from $27.3 million

## Summary
Severity: Critical
Target: Step Finance
Loss: $27,300,000
Published: 1/31/2026
Source: https://rekt.news/step-finance-rekt
Type: rekt-postmortem

## Details
## Step Finance - Rekt

 Wednesday, February 4, 2026 Step Finance - Admin Privileges - Rekt 

 read this article also in : 

 Ninety minutes and one compromised laptop separated Step Finance from $27.3 million . 

 The smart contracts worked flawlessly. The humans didn't. 

 Just someone's executive device getting owned by what the team called "a well known attack vector" - the kind of phrasing that screams phishing email without actually saying it.

 Step Finance had checked all the boxes: Audited contracts, bug bounties, public security reviews , a Solana-focused media outlet , and plans to tokenize equities on Solana.

 261,854 SOL unstaked and gone before breakfast, leaving their STEP token down 93% and their "front page of Solana" branding aging like milk in the summer sun.

 CertiK flagged the bleeding while Step Finance scrambled for cybersecurity DMs , eventually recovering $4.7 million through Token22 protections - a consolation prize on a $27.3 million education. 

 When your code passes every audit but your executives fail basic email hygiene, what exactly are security reviews protecting? 

 Credit: CoinTelegraph , StepFinance , Piotr Rzonsowski , CertiK , Chainalysis , coingecko , Remora Markets , SolanaFloor , Peckshield 
 January 31st started quietly enough. 

 Early morning brought the first public sign of trouble - Step Finance admitting on X that "there has been a breach of security for some of our treasury wallets hours ago."

 The attack had already finished its work while the disclosure was still being drafted.

 Minutes later came the desperate follow-up : "We are contacting Cybersecurity firms to assist. Any firms who can assist feel free to slide into DMs."

 By late morning, the story had evolved into something more palatable for public consumption - "sophisticated actor during APAC hours" executing through "a well known attack vector." 

 Sophisticated actor. Well known attack vector. 

 Translation: Someone phished an executive and walked away with the treasury.

 CertiK's alert told the real story - 261,854 SOL had been unstaked after "stake authorization had been transferred" to a fresh wallet. On Solana, unstaking requires direct wallet permissions. No exploit needed when you already have the keys.

 Step Finance wasn't hacked. Step Finance was handed over. 

 If the attackers needed sophisticated techniques, why did basic key compromise work just fine? 

## The Laptop That Ate $27.3 Million

 February 2nd brought the confession nobody wanted to hear . 

 "This was a result of our executive team's devices being compromised." 

 Not a zero-day. Not a supply chain attack on some obscure dependency. Not even a rogue insider with a grudge and a hardware wallet.

 Executive devices. Plural. Compromised.

 Step Finance built the dashboard. They ran the validator. They acquired Moose Capital and rebranded it Remora Markets to bring tokenized equities to Solana. They hosted conferences . They built a media outlet . 

 And somewhere along the way, someone on the executive team opened the wrong email, clicked the wrong link, or approved the wrong transaction. 

 QuillAudits put it plainly : "most likely a social engineering attack."

 The 2025 playbook - where private key compromises drove 88% of Q1 losses alone - carried right into 2026 without missing a beat.

 Step Finance had audited contracts, bug bounties and public security reviews . The kind of security posture that looks great in a pitch deck.

 None of it mattered when the attack vector was a human being with inbox access and signing authority.

 Piotr Rzonsowski’s incident thread laid out the operational failures with surgical precision : Weak key management, insufficient access controls, no monitoring during off-hours, single points of failure.

 Piotr’s full writeup sharpened the knife : "Step Finance's hack is a reminder that security is a chain, and chains break at the weakest link."

 Step Finance learned this lesson at a $27.3 million tuition rate - though they managed to claw back $4.7 million through Token22's built-in security protections on Remora assets.

 The keys walked out the door. The SOL followed. 

 Where exactly did those 261,854 SOL go after the executive laptops gave up the keys? 

## Following the Breadcrumbs

 CertiK's on-chain analysis painted a clean picture of the heist mechanics. 

 Stake authorization got transferred to a fresh wallet address: 
 LEP1uHXcWbFEPwQgkeFzdhW2ykgZY6e9Dz8Yro6SdNu 

 From there, the unstaking began. 261,854 SOL - worth $27.3 million - methodically pulled from Step Finance's treasury and fee wallets.

 Unstaking Transaction: 
 5EeXqPQci3ZnbFGWPJf622cLqLGnMuNcAr1rDGCizKRFt9owawCzovNpBC4xNh7A4a5p7Qkvsg8nPaYmw3MiYCvF Then came the main event.

 Key withdrawal transaction (261,932 SOL): 
 4Ly35PsVTBNPVibpDRww6FC43pU5Tuw6UtaKECzcLKXtWTPyyvw1dw8LoNRLBDMgQUP81nN69mhiAEDJvzL8X317 

 The operation wasn't a solo act.

 A secondary wallet joined the party: 
 7raxiejD8hDUH1wyYWFDPrEuHiLUjJ4RiZi2z1u2udNh 

 QuillAudits confirmed that the majority of stolen funds remain parked in the attacker's accounts . Those are currently being held in one of the wallets mentioned, the secondary wallet used in the attack. 

 No frantic bridge hopping. No Tornado Cash deposits showing up in the transaction logs yet. Just a patient wallet waiting for the heat to cool. 

 The numbers tell different stories depending on who's counting.

 Step Finance claimed "approximately $40M" in losses , but on-chain evidence tells a simpler story of just one theft, 261,932 SOL , roughly $27.3 million at the time of extraction.

 The extra $13 million exists only in Step Finance's press release. Maybe they will release a proper post-mortem that reveals the missing link.

 Step Finance managed to recover $3.7 million in Remora assets through Token22's built-in security features, plus another $1 million in other positions . A $4.7 million clawback on a ~$27 million drain - roughly the same success rate as finding your car keys after the car's already been stolen.

 The funds sit visible on Solscan , public as a billboard, untouchable as smoke. 

 What happens to a protocol when its treasury evaporates but its token holders remain? 

## Ninety-Three Percent Down

 STEP didn't crash. STEP cratered . 

 From $0.023 to $0.001578 in under 24 hours - a 93.3% nosedive that turned governance tokens into collectible dust. 

 Panic selling hit before Step Finance could even finish drafting their first disclosure. By the time "sophisticated actor" and "well known attack vector" made it into the official narrative, the market had already delivered its verdict.

 Step Finance's response landed February 2nd with the weight of a protocol fighting for survival: 

 "At this time, we do not recommend anyone engage with the STEP token until our investigation is complete." 

 Translation: Don't touch it, we're figuring out if there's anything left to save.

 A pre-exploit snapshot would determine who gets made whole - or at least partially whole - assuming there's a path forward that doesn't involve the word "defunct."

 The damage rippled beyond Step's own walls. Remora Markets , the tokenized equities platform Step acquired as Moose Capital in late 2024, found some of its rStocks tangled in the stolen treasury assets . Step Finance had been Remora's largest liquidity provider - now that relationship was a liability.

 Remora moved quickly to reassure users that all rTokens remained "backed 1:1 with our broker" while LP activities paused pending system security.

 The silver lining : All Remora rStocks involved in the incident were eventually recovered through Token22's built-in protections.

 SolanaFloor , Step's media arm , kept publishing . The Solana Crossroads ( powered by SolanaFloor ) conference remains in the plans for 2026 ( according to their header ). But the ecosystem that Step Finance had spent years building now carried an asterisk the size of $27.3 million.

 The question now is whether Step Finance can beat the odds.

 Immunefi CEO Mitchell Amador offered the industry's grim prognosis : "Nearly 80% of crypto projects that suffer a major hack fail to fully recover."

 Not because of the money lost. Because of the trust burned. 

 Does Step Finance beat those odds, or does their front page become a memorial page? 

 Over $4 billion vanished from crypto in 2025 - and the culprit wasn't just buggy code. 

 Private key compromises accounted for 88% of all Q1 2025 losses according to Chainalysis . 

 Wallet compromises drove $1.71 billion in theft during the first half alone . The pattern couldn't be clearer: humans remain the industry's most exploitable vulnerability, and the gap is widening.

 Step Finance added $27.3 million to that ledger not because their smart contracts failed, but because someone's inbox did.

 Audits can verify code. Bug bounties can incentivize white hats. Security reviews can stress-test logic. 

 None of it matters when the person holding the keys clicks the wrong link on the wrong morning.

 The industry keeps building better locks while attackers simply ask for the keys - and keep getting them.

 Step Finance wasn't the first protocol to learn that lesson at eight-figure tuition rates, and January 2026's $370 million in total losses suggests they won't be the last. 

 How many more treasuries need to empty before the industry realizes the biggest vulnerability isn't in the code - it's checking email? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
