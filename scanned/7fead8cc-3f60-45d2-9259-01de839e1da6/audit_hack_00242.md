# [H] Solv exploit: Counting the same Bitcoin twice wasn't enough

## Summary
Severity: High
Target: Solv
Loss: $2,730,000
Published: 3/5/2026
Source: https://rekt.news/solv-rekt
Type: rekt-postmortem

## Details
## Solv - Rekt

 Tuesday, March 10, 2026 Solv - BRO - ERC-3525 

 read this article also in : 

 Counting the same Bitcoin twice wasn't enough. Now they're minting the same tokens twice too. 

 Solv Protocol's BitcoinReserveOffering contract shipped without an audit, without bug bounty coverage, and apparently without anyone asking what happens when a callback fires before the books are balanced. 

 On March 5th, someone asked. 135 BRO tokens went in. 567 million came out. 38 SolvBTC, roughly $2.73 million, walked out the door in a single transaction, looped 22 times over.

 Solv called it a "limited exploit." Fewer than 10 users were affected. Funds will be covered. Security partners were notified.

 All the right words, in all the right order, the same playbook they ran when their Twitter got hacked in January 2025 , the same month Rekt documented their creative Bitcoin accounting .

 Third incident in fourteen months, third time the response sounded like a press release drafted before the damage was counted.

 The attacker didn't stick around to negotiate the 10% white hat bounty . The funds are in RailGun now . 

 When you call yourself the largest on-chain Bitcoin reserve , how does one unaudited contract become the crack that swallows $2.73 million? 

 Credit: DefimonAlerts , Solv Protocol , DeepNewz , QuillAudits , Pyro , Chris Dior , SherlockVarm , EIP , upside , The Block , AMLBot , RareSkills , HackenProof , Godiex , Cryptopolitan , forklog 
 March 5th, DefimonAlerts fired the opening shot , a crisp, technical breakdown posted to X before most people had finished their morning coffee. 

 The alert named the contract , named the flaw, named the transaction.

 Decurity's automated monitoring bot had caught the double-minting pattern and traced it back to the BitcoinReserveOffering (BRO-SOLV-20MAY2026) contract . No ambiguity, no hedging. The attacker had already finished by then.

 Hypernative Labs, SlowMist, and CertiK would later be credited by Solv for "promptly alerting" them .

 Solv's official response landed on X shortly after. Measured. Controlled.

 Almost suspiciously polished for a team that had just watched $2.73 million walk out the door : "A limited exploit occurred in one of our BRO vaults, affecting a very small number of users (<10). The impacted amount is 38.0474 SolvBTC. All other vaults and user funds remain secure and unaffected." 

 Fewer than 10 users. Limited exploit. Funds will be covered. Security partners notified. Each phrase doing exactly the work it was designed to do, contain the story, shrink the blast radius, project calm. 

 They even offered the attacker a 10% white hat bounty , posting a contact address like a ransom note written by a PR firm.

 No on-chain response came. No funds returned. By the time the community finished reading Solv's statement, the attacker had already converted to ETH and disappeared into RailGun .

 Pseudonymous researcher Pyro was among the first to put a name to the mechanism - he described it as a self reentrancy attack, the same class of exploit that's been draining DeFi protocols since 2016.

 CD Security co-founder Chris Dior confirmed the loop mechanics independently : 22 cycles, 135 BRO in, 567 million out.

 Then SherlockVarm dropped the detail that reframed the narrative : "This contract was introduced without an audit. Also, the Solv Protocol bug bounty program only covers Web2 infrastructure and Solana contracts."

 Not a novel vulnerability. A known attack class, in an unaudited contract, excluded from the bug bounty program , while Solv's Audit page lists 5 auditors as proof of their security commitment .

 The audits were real. The contract just wasn't in any of them. 

 If the contract was never in scope, what exactly were those audits protecting? 

## Two Mints, One Deposit

 The vulnerability wasn't buried in cryptographic complexity or hidden behind layers of abstraction. 

 It was sitting in the minting logic, waiting for someone to read the execution order carefully. 

 Here's how the BRO vault was supposed to work: A user deposits collateral, the contract mints BRO tokens representing their position, everyone goes home with the right amount. Simple enough on paper.

 The rot was in the ERC-3525 NFT transfer logic during minting . ERC-3525 is a semi-fungible token standard built on top of ERC-721, think of it as the middle ground between a unique NFT and a divisible ERC-20.

 Each token has an ID like a traditional NFT , but also carries a numeric value that can be split, merged, and transferred in fractions, making it well-suited for representing fractional ownership of yield-bearing positions like BRO vaults.

 Ambitious on paper. Dangerous in practice when nobody bothers to handle the edge cases. 

 Worth noting: ERC-3525 was designed by Ryan Chow and the Solv Protocol team themselves , Chow is listed as a co-author on the official Ethereum Improvement Proposal , and Solv was the first protocol to deploy it at scale. 

 The standard they built is the standard that bit them. It's also what made the callback dangerous, because ERC-3525 inherits ERC-721's transfer mechanics, every NFT movement triggers onERC721Received, and in Solv's implementation, that trigger minted tokens before the books were balanced. 

 When a user called mint() and transferred an NFT as part of the deposit, the contract used doSafeTransferIn to move it, triggering the onERC721Received callback in the process.

 Solv's implementation used that callback to mint BRO tokens to the attacker. 

 Then execution returned to mint(). Which minted BRO tokens to the attacker again. 

 Same deposit. Same exchange rate. The attacker managed to pull off a double mint . 

 No exploit toolkit required. Just a callback that fires before the function that called it has finished.

 The attacker started with 135 BRO tokens. They burned those through the reserve contract, receiving 0.000031102085070226 GOEFS tokens in exchange. 

 Then they called mint(), sending the GOEFS tokens back in alongside NFT ID 4932. The callback fired, minted BRO . Execution returned to mint(), minted BRO again . Two mints for the price of one deposit.

 Because the entire sequence ran inside a single transaction, the exchange rate never updated between loops. The attacker burned the freshly minted BRO, received GOEFS, called mint() again -same rate, same double-mint, larger stack. Twenty-two times in one transaction. 

 135 BRO became 567 million : 0x44e637c7d85190d376a52d89ca75f2d208089bb02b7c4708ad2aaae3a97a958d 

 From there, the exit was surgical.

 The attacker used 165M of the 567M BRO , swapping them for SolvBTC through the BRO-SolvBTC exchange, then routing SolvBTC → WBTC → WETH → ETH via Uniswap V3, converting 38.0474 SolvBTC into 1,211 ETH across attacker-controlled wallets.

 The attacker transferred the stolen ETH to two intermediary addresses before routing it toward RailGun , the standard pre-laundering hop.

 It didn't work. RailGun's KYT and AML checks flagged the deposit and returned the funds to the sender. The screening mechanism designed to keep known malicious addresses out of the privacy pool worked exactly as intended. 

 So the attacker went to Tornado Cash instead . 

 After receiving the funds back, the attacker transferred them to several addresses, converted WETH back to ETH, and deposited into Tornado Cash. The sanctioned mixer carries no such compliance filters.

 The irony writes itself: The compliance-focused privacy protocol held the line; the sanctioned one didn't.

 Victim contract (BRO Token): 
 0x014e6F6ba7a9f4C9a51a0Aa3189B5c0a21006869 

 Attack Transaction: 0x44e637c7d85190d376a52d89ca75f2d208089bb02b7c4708ad2aaae3a97a958d 

 BRO-SolvBTC Exchange: 
 0x1E6101728fD9920465dfA1562c5e371850103da2 

 Attacker EOAs: 
 0xa407fe273db74184898cb56d2cb685615e1c0d6e 0x9f7a6b16d0d9824197651f33506e3a2bb2f6f432 0xd17ddd34c414f666fc51e9fe04d32cf60eda78fe 

 The real damage - 38.0474 SolvBTC drained from the protocol, roughly $2.73 million - was done before most people knew it had started. 

 QuillAudits called the root cause "a missing guard against double minting" and noted the importance of carefully handling external calls, callbacks, and state updates. 

 SherlockVarm put it more plainly : "Following basic security best practices here could have likely prevented this exploit."

 The basics in question are well-established, when onERC721Received callbacks fire during a mint, a check-effects pattern or a reentrancy guard on the mint function closes the window entirely. Neither was present.

 The fix is a few lines of code. The oversight cost $2.73 million. 

 When the contract that drains you was never on anyone's list, what exactly were the audits for? 

## Audited, Except Here

 Solv's audit record includes five firms : Quantstamp, Salus, OpenZeppelin, Offside and Paladin. 

 Real audits, by credible firms, covering real contracts. Each one a genuine commitment to security on the code they were given. 

 None of them audited the BitcoinReserveOffering contract.

 The BRO vault was a newer product (less than a year old), part of Solv's expanding suite of structured yield offerings, introduced after the bulk of those audits were completed. Somewhere between product launch and production deployment, the security review got skipped. Not delayed. Not scheduled. Skipped.

 SherlockVarm identified the gap immediately after the exploit: The contract went live without an audit, and the bug bounty program on HackenProof told the same story, two active programs, one covering Web2 infrastructure, one covering the Solana contract.

 The EVM contract that just lost $2.73 million was not covered. 

 A researcher who found the double-mint flaw before the attacker did would have had nowhere legitimate to report it for a reward. 

 This wasn't Solv's first time navigating a security headline, either.

 January 1st, 2025 : User Godiex watched 0.01 BTC vanish from their SolvBTC.BBN position without a single signed transaction.

 The funds reappeared in two new wallets , still collecting Solv points, just no longer under the original owner's control. SolvBTC had marketed the product as self-custodial.

 The following days, Solv faced a public controversy over how it counted TVL. 

 Critics alleged the protocol was using pre-signed transactions to record the same Bitcoin across multiple protocols simultaneously , booking signed promises as reserves without the underlying BTC ever moving. 

 Solv disputed the allegations.

 Ryan Chow responded directly : "For months we are aware competitors are out there smearing us to our partners and persuade them 'don't work with Solv, work with us instead.' We have so far chosen to ignore and continue doing us. But no more. Make no mistake. This is a smear campaign, coordinated and orchestrated, and going to great lengths in attempt to take Solv down. This. Is. War. But we will Solv it."

 Then, on January 5th, right in the middle of that controversy, Solv's official X account was compromised . Hackers posted a fraudulent Ethereum address.

 Solv pulled the post within 15 minutes and covered user losses. 

 The Twitter compromise happened at the peak of the TVL controversy. Convenient timing, or just chaos, either way, the pattern was already forming - incident, polished response, back to business. 

 First they got called out by critics for effectively counting the same Bitcoin more than once through pre‑signed transactions and TVL games. Then they shipped a vault where the same tokens could be minted twice, and an attacker proved it on‑chain.

 What Solv built was the appearance of a security infrastructure: brand‑name firms, each covering a defined scope, but none of the published audits included the BitcoinReserveOffering contract that just got drained.

 The “Bitcoin Reserve Offering” name evokes institutional‑grade architecture, and many users would reasonably assume those contracts had been scrutinized like the rest of the protocol.

 They would have been wrong. 

 When your incident history and your audit gaps grow at the same pace, at what point does the pattern become the product? 

 The self-proclaimed largest on-chain Bitcoin reserve. Drained through an unaudited contract, via an attack class documented since 2016. 

 The co-founder once declared war on the TVL controversy , “a smear campaign by competitors”, he said. 

 The math failed anyway. One deposit minted twice in the contract.

 SOLV went up 3.5% on the day of the exploit. The market has learned to read the "we'll cover it" statement as a buy signal, and Solv has learned that a polished incident response is worth more than a security review.

 Fewer than 10 users affected, losses covered, statement issued, the blast radius managed so cleanly it barely registered as news.

 The attacker walked away with $2.73 million, tried RailGun first, got rejected by its own compliance filters , then routed everything through Tornado Cash instead.

 Solv didn't get exploited despite their security infrastructure. They got exploited because the infrastructure had a door nobody was watching, and nobody was watching because nobody thought to check whether it was there. 

 When the largest on-chain Bitcoin reserve can't be bothered to audit every contract that touches user funds, what exactly does "reserve" mean? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
