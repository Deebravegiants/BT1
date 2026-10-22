# [H] IoTeX exploit: On February 21, 2026, an attacker quietly obtained the owner key to IoTeX's ioTube bridge validator contract, and with it, administrative control over

## Summary
Severity: High
Target: IoTeX
Loss: $4,400,000
Published: 2/21/2025
Source: https://rekt.news/iotex-rekt
Type: rekt-postmortem

## Details
## IoTeX - Rekt

 Wednesday, February 25, 2026 IoTeX - Private Key Leak - Rekt 

 read this article also in : 

 One compromised private key. One Saturday morning. One bridge that handed over the keys to everything it was supposed to protect. 

 On February 21, 2026, an attacker quietly obtained the owner key to IoTeX's ioTube bridge validator contract, and with it, administrative control over every asset the bridge was holding. 

 No exploit. No zero-day. No clever math. Just a single key in the wrong hands, and a four-step execution that drained $4.4M in real bridged assets from the TokenSafe and minted 410 million unbacked CIOTX tokens on top of it.

 Onchain investigator Specter was first to flag the bleeding , reporting $4.3M drained.

 PeckShield escalated to $8M within ninety minutes.

 By the time IoTeX co-founder Raullen Chai told The Block the losses were "around $2M," three different numbers were already circulating and none of them were wrong, they were just counting different things.

 Here's what actually happened: The attacker physically stole $4.4M in real assets - USDC, USDT, WBTC, WETH, IOTX, PAXG, DAI, BUSD, and UNI - directly from the bridge reserves.

 According to Defimon Alerts , they minted 821 million CIOTX (~$4.09M) and 9.3 million CCS tokens ( deprecated tokens with no market value, per Chai ) out of thin air using the same stolen access. 

 IoTeX's own accounting later cited 410M CIOTX , a figure the on-chain mint record does not support. 

 10 confirmed mint transactions on Ethereum , that total roughly 821M. IoTeX has not explained the discrepancy.

 IoTeX's $2M "net loss" claim rests on their assertion that 86% of those minted tokens are now frozen on-chain with no liquidity and can't be moved.

 The number that doesn't require trusting anyone: 66.77 BTC (~$4.29M) sitting in four freshly created Bitcoin wallets, visible to anyone with a browser, untouched as of February 23.

 IOTX dropped 22% on the news (from $0.0054 to below $0.0042) , trading near $0.00467 as of February 24 - roughly 98% below its all-time high of $0.255 set in November 2021 .

 South Korea's Upbit placed IOTX on its trading alert list and suspended deposits.

 IoTeX distributed an emergency patch to chain delegates to blacklist attacker addresses , consensus would resume automatically once enough patched delegates came online, suspended the bridge pending a full independent audit , and began coordinating with exchanges to freeze what they could.

 Their L1 chain is currently back online .

 The attacker, meanwhile, had already moved through THORChain and is holding stolen assets on Bitcoin . 

 When a single key can silently transfer ownership of every contract in your bridge stack, what exactly is the security model protecting? 

 Credit: Specter , PeckShield , The Block , IoTeX , Defimon Alerts , CoinDesk , CoinGecko , Wublock , Beosin Alert , QuillAudits , The Crypto Times , CRYIP , 𝟘xpaiN Σ , Trade Brains , Chainalysis 
 Specter fired the first warning shot on February 21st. 

 "The private key of IoTeX may have been compromised, resulting in their token safe being drained for a total loss of approximately $4.3M."

 USDC, USDT, IOTX, WBTC, BUSD drained . Stolen assets already swapped into ETH, with 45 ETH bridged to Bitcoin . Three attacker addresses published . The alert was clean, specific, and landed while most of the industry was asleep.

 Ninety minutes later, PeckShieldAlert escalated the number . 

 "The IoTeX[.]io Bridge has been hacked for over $8M worth of crypto due to a compromised private key. The hacker has swapped the stolen funds to $ETH and has started bridging them to BTC via Thorchain." 

 The jump from $4.3M to $8M wasn't a correction, it was a wider lens. Specter had counted what left the vault. PeckShield may have counted what the attacker minted on top of it . Both were right. They were just measuring different parts of the same operation.

 DefimonAlerts filled in the technical picture shortly after , putting the gross estimate at $8.46M and naming the contract at the center of it: The TransferValidatorWithPayload. The attacker had seized ownership of both the bridge's TokenSafe and its MinterPool . They drained one and printed from the other.

 IoTeX's first public response came 79 minutes after Specter's alert .

 "Our team is fully engaged, working around the clock to assess and contain the situation. Initial estimates indicate the potential loss is significantly lower than circulating rumors suggest."

 No figure. No technical detail. No acknowledgment of what had already been mapped on-chain by three separate security firms. Just the assurance that the situation was under control, posted while the attacker was still actively bridging funds through THORChain.

 A few hours later, IoTeX had a number : $2M. Co-founder Raullen Chai told The Block the same figure directly - "around $2M USD for now" - and added that the minted tokens were " of little consequence. "

 Eight hours had passed since the first alert. The attacker had been done with the drain phase for most of them.

 The gap between what the chain showed and what the team said would define how this story got told everywhere else. 

 When three security firms have already mapped your exploit before your first statement drops, what does your response timeline actually tell users about your monitoring infrastructure? 

## Pwned by Access

 IoTeX's bridge wasn't exploited. It was administered - by someone who shouldn't have been holding the keys. 

 At the center of the attack sat a single externally owned account: The owner of the TransferValidatorWithPayload contract on Ethereum.

 That EOA had one critical privilege, the ability to call upgrade(). In the right hands, a routine maintenance function. In the wrong ones, a master switch.

 Compromised Validator Owner EOA: 
 0x6dd31a526eE3DdBC7BE888b729A445695c03148e 

 TransferValidatorWithPayload Contract: 
 0xE7eBA1CEA51EC9B3AcCC16728e3B8786560c59d5 

 Ownership Transfer Transaction: 

 0xe9e7f33ebfe2230c147e6e0321f5f2c7de1b89fe9fc08830fc3f8ac5845bc9f0 

 The attacker called upgrade() and pushed a malicious contract version in its place - one that had been stripped of every signature check and validation requirement the original contained. 

 Upgrade Transaction: 

 0xc9c53b28a2aec4f8641394d2ba086a4d0b0a93e40d0a86c578c7fc20ab6351b8 

 The bridge's own upgrade path became the entry point. 

 With the validator layer replaced, ownership of the TokenSafe and MinterPool transferred cleanly to attacker-controlled addresses.

 No alarm. No threshold. No second signature required. The contracts simply obeyed their new owner.

 QuillAudits put it plainly : This was not a smart contract exploit. Just compromised trust at the ownership layer.

 How the key was obtained remains publicly unconfirmed. 

 IoTeX's own statement described "a sophisticated, long-planned attack by professional actors targeting multiple chains," with Chai telling The Block the operation showed signs of preparation spanning six to eighteen months . 

 That timeline points toward something more deliberate than a phishing click, possible insider access, a long-horizon social engineering campaign, or infrastructure infiltration that went undetected for over a year.

 The structural failure underneath it is harder to excuse than the key loss itself.

 A single EOA held unchecked upgrade authority over contracts that custodied millions in bridged assets, with no multisig requirement, no timelock, and no circuit breaker that could intervene between the attacker calling upgrade() and the drain beginning.

 The architecture assumed the key would never be compromised. It had no answer for when it was. 

 If eighteen months of preparation can quietly dismantle a bridge from the inside, how many other validator keys are already in the wrong hands right now? 

## Drain, Mint and Exit

 189 transactions on a Saturday morning . The attacker didn't linger. 

 Phase one was the drain. With ownership of the TokenSafe secured, every bridged reserve asset moved out in rapid succession - nine tokens, according to IoTex’s Security Incident Update : 

 1,36K USDC 
 1,14K USDT 
 635 WETH 
 6.12 WBTC 
 20,159 DAI 
 8.72 PAXG 
 13.85M IOTX 
 45,825 BUSD 
 2,835 UNI 

 Total out of the TokenSafe: ~$4.4M . Real assets, real value, gone.

 Phase two was the mint. The MinterPool produced 821 million CIOTX across 7 transactions, confirmed on-chain by Rekt News, routed to three beneficiary addresses: 

 CIOTX Mint Beneficiary #1: 
 0xa467a6c7ca8e812e997bfe50ce4e7991aad00a88 

 111,111,000 CIOTX in 3 mint transactions. 

 1,100,000 CIOTX Minted: 
 0x1211c49c178446f6952781f136b212383db92ac22257e2bb6d1d7fa4372aaf11 

 110,000,000 CIOTX Minted: 

 0x02dde64548455b26b437a25e653cc6e399af3dc4f75698a94d5164b0d161251f 

 11,000 CIOTX Minted: 
 0x1738b63ceebdb9c16da62edad6586ef4c15ed7856bb80104dd7bc19353a8e6d3 

 CIOTX Mint Beneficiary #2: 
 0x43ed5caadb3fbef610dad8aae621519b20b34de6 

 610,000,000 CIOTX in 2 mint transactions. 

 110,000,000 CIOTX Minted: 
 0x4b532369f06e56bba9d4765c377de5d3336ba9b78b49005af06a6d32fa6eec82 

 500,000,000 CIOTX Minted: 

 0xa40a1a464bf317c0fa023d285109b768d9f81a971820324baaa80c33a6f77350 

 CIOTX Mint Beneficiary #3: 
 0xc9ca98967cc0f9ffb36c9752e8d7536f6b815c1b 

 100,000,000 CIOTX in 2 mint transactions. 

 50,000,000 CIOTX Minted: 
 0x0aa445c34b989884f5f252dfd320ffd9f937fad4b27d71635691d4bb3402c8a1 

 50,000,000 CIOTX Minted: 
 0xc9ce7bb9dfb19d9b6e27485725a8fb76d820a323f433f2ad509b1c57586e5520 

 The 821M figure from DefimonAlerts is confirmed by the on-chain mint record, all 7 transactions on Ethereum, as noted above in detail.

 IoTeX's own Feb 22 statement cited 410M CIOTX , a figure that remains unexplained given the on-chain evidence.

 The discrepancy may reflect burns or freezes between mint and accounting, an incomplete trace at time of reporting, or deliberate framing, IoTeX has not addressed it directly.

 The attacker also minted 9.3 million CCS tokens , which remain unspent in the secondary exploit EOA.

 Combined mint-time value: Could be $8 million on paper - though Chai would later tell The Block that CCS tokens are "deprecated long time ago so have no value." 

 If we were to go by Coingecko’s stats, which could be out of date, the minted totals would add up to the following… 

 821 Million CIOTX : $3.7 Million

 9.3 Million CCS : $4.3 Million

 Hypothetical Total of Minted Tokens(As of February 25th): $8 Million 

 Whether that number reflects real exit liquidity is a separate question entirely.

 Both phases funneled through two primary exploit addresses. 

 Primary Exploit EOA: 
 0x6487B5006904f3Db3C4a3654409AE92b87eD442f 

 Secondary Exploit EOA: 
 0xE6A191a894dD3c85e3c89926e9f476F818eE55d9 

 From there, everything got converted. Uniswap and other DEXs absorbed the diverse basket of stolen tokens and returned ETH. 

 Then came THORChain - no KYC, no custodian, no freeze mechanism. The ETH moved through a network of relay wallets and out the other side as Bitcoin , clean and cross-chain, landing in four Bitcoin addresses that hadn't existed before February 21st. 

 ETH Relay / DEX Swap Hub (used for DEX swaps and THORChain outbound): 
 0x39c188029433bdd7965B55959221ABe00466565E 

 Frozen ETH Relay (~$248K recovered by exchanges): 
 0xa5f24f4f89f62dd2df9a4a46b9f81f6590025d97 

 0xOwnerpaiN tracked them down one by one as the funds arrived, publishing each address as the inflows hit. 

 BTC Destination Wallet #1: 
 135oSa2fobTxtHtm5dwTREDyRY2o1DG1Aw 

 14.37 BTC - ~$967K - confirmed balance as of February 25th. 

 BTC Destination Wallet #2: 
 16xusPKLMyqK68SkhfXDtic6AJPDi51tqh 

 19.97 BTC - ~$1.34M - confirmed balance as of February 25th. 

 BTC Destination Wallet #3: 
 12V7jhcPnqnGbRFMasSW2CZVBd8qpvUgAK 

 13.77 BTC - ~$926K - confirmed balance as of February 25th. 

 BTC Destination Wallet #4: 
 1PN2BoHU4buDQWcrNHk9T9NBA2qX8oyYEc 

 18.66 BTC - ~$1.25M - confirmed balance as of February 25th - the largest wallet, fed from 3 separate ETH sources. 

 Combined total across all four: 66.77 BTC (~$4.49M) - confirmed on-chain as of February 25th.

 The attacker parked everything and went quiet. No cash-out attempt. No mixer. No further hops.

 Just four Bitcoin addresses sitting still, visible to anyone with a browser, while the investigation clock runs.

 One detail 𝟘xpaiN Σ caught live : Wallet #2 was still actively receiving funds during his tracking window - growing from 14.2 BTC to 19.96 BTC as the attacker continued converting ETH through THORChain even after the breach was public. The drain was done. The laundering was still in motion.

 Four Bitcoin wallets. 66.77 BTC. Zero outgoing transactions. 

 What exactly is the attacker waiting for? 

## Still Counting

 On February 22, IoTeX published the most substantive statement of the entire incident - a formal recovery roadmap that finally named the figures the team had been dancing around for two days. 

 The numbers according to IoTeX: $4.4M drained from the bridge reserves (TokenSafe). 410M CIOTX minted via MinterPool - IoTeX's figure , which the on-chain mint record puts at 821M.

 Of those minted tokens, IoTeX claimed 86% were already locked or frozen through chain-level controls - 315M CIOTX trapped on Ethereum and Base with no bridge path, 40.5M remaining in attacker wallets on the IoTeX chain that are currently blacklisted, and 52.4M deposited to Binance where the team said it was actively working to freeze.

 Only 1.7M CIOTX - 0.4% of the total minted - had been swapped on DEX and was considered unrecoverable.

 If those figures hold, the math behind IoTeX's $2M net loss claim becomes more defensible. 

 The problem is that "if" is doing significant work. The Binance freeze status has not been independently confirmed. 

 The chain-level blacklisting of 29 attacker-controlled addresses is a unilateral action by IoTeX against its own chain. 

 And the non-IOTX assets - the $4.4M in USDC, USDT, WBTC, WETH, and the rest pulled from the TokenSafe - converted to approximately 2,183 ETH and routed to Bitcoin via THORChain , remain entirely in attacker hands.

 That part of the story does not have a recovery chapter yet.

 One exception worth noting: The 9.3 million CCS tokens minted via the secondary exploit EOA - the mystery position - are still sitting unspent in that address . The attacker hasn't moved them.

 The chain-listed value shows ~$4.3M, but Chai told The Block directly that CCS is "deprecated long time ago so have no value." 

 Whether the Etherscan price is a ghost, a stale feed, or a thin illiquid market, the practical exit value appears to be near zero. 

 The attacker may be sitting on a nominally large position that is effectively worthless, or may have known that all along and moved on to what actually mattered: The TokenSafe drain and the BTC already parked in four wallets.

 The Feb 22 statement also carried a white-hat bounty offer .

 On February 23, IoTeX formalized the offer to CoinDesk : $440,000 (10%) in exchange for the return of ~$4.4M within 48 hours, with a pledge of no legal action and no sharing of identifying information with law enforcement.

 IoTeX announced they had flagged the primary exploit address on Etherscan as Fake_Phishing2054654 and sent an on-chain message directly to the attacker. 

 The onchain message reads : "This is regarding the ioTube bridge exploit on Feb. 21, 2026. All fund movements across Ethereum, IoTeX, and bitcoin have been fully traced." 

 No response has been reported as of February 25th. The 48-hour deadline that expires today.

 Onchain Message: 

 0x451c8c62d1fbc08258a0eaad73668e1ad75fd4d57caa3da4f16f1d060397f98f 

 SpecterAnalyst flagged something else in the aftermath that the team's statement never addressed directly: A wallet funding trail connecting the IoTeX attacker's EOA to the $49.5M Infini stablecoin hack from February 2025. 

 The Infini case involved a former contract developer who retained admin privileges after their engagement ended , then executed a delayed drain using the same operational playbook - insider key access, deferred execution, cross-chain laundering through Tornado Cash.

 Chai's comment to The Block about "a planned attack that could have been developing for six to eighteen months" lands differently with that context.

 No formal attribution has been made by law enforcement or any analytics firm as of February 23. 

 Outside experts are skeptical that the real losses - the TokenSafe assets already converted and BTC-bridged - are coming back. 

 Nick Motz, CEO of ORQO Group, told CoinDesk : "Containment is not the same as recovery. The assets with actual market value were swapped and bridged. Those are, in my assessment, unlikely to be recovered."

 Nanak Nihal Khalsa, co-founder of human.tech, offered a matching verdict : "It's hard to predict how much, if any, can be recovered."

 The promises on the table as of this writing: A detailed compensation plan for affected bridge users, a community AMA with the founding team, a full post-mortem report, expedited implementation of IIP-55 to decentralize bridge validation through a multi-party validator set, new mandatory multisig and 24-hour timelock controls for all validator keys, and an expanded bug bounty program.

 IIP-55 is the exact architectural fix that would have made this attack significantly harder to execute - a proposal drafted in December 2025 , two months before the hack, now being rushed because the vault is empty. 

 What's been promised and what's been delivered are still two different lists. The token market didn't wait to find out which one would be longer. 

 The L1 at least has a resolution. On February 24 at 06:06 AM UTC, IoTeX confirmed the chain was back online with v2.3.4 deployed - permanently blacklisting all 29 attacker wallets at the network level.

 The same update named the FBI explicitly for the first time, confirmed a formal response to DAXA (the Korean Digital Asset Exchange Association), and committed the IoTeX Foundation Treasury to 100% compensation for all affected bridge users.

 The bridge remains paused pending an independent security audit with no timeline given. 

 When the compensation plan, the AMA, the post-mortem, and the governance reform are all still pending, what exactly has been resolved? 

 Another bridge. Another private key. Another vault that was one key away from being someone else's. 

 The method that took down IoTeX's ioTube is the same method that took down Infini , Step Finance , and a growing list of protocols that did everything right on paper - audited contracts, public security reviews, years of operational history - and still found themselves watching their vaults empty out because one key ended up somewhere it shouldn't have. 

 How that key moved from IoTeX's infrastructure to an attacker's wallet remains publicly unanswered, and if the pattern holds, it may stay that way.

 Private key compromises rarely get the clean post-mortem that code exploits do, because admitting your humans failed doesn't come with a patch.

 IoTeX's response was fast - the February 22 comprehensive statement , the v2.3.4 chain patch , the Binance coordination. At least they moved. 

 But 66.77 BTC (~$4.29M) is sitting on Bitcoin untouched, the compensation plan is still a promise, and IIP-55 - the governance reform that would have made this attack architecturally harder - existed before the vault emptied and wasn't prioritized until after it did. 

 According to Chainalysis, private key compromises drove 88% of all crypto stolen in Q1 2025.

 The industry has known this for a while now.

 The attack surface isn't just the code anymore - it's whoever is holding the keys, on whatever device, checking whatever email, on whatever Saturday morning the attacker has been patiently waiting for. 

 When the most dangerous vulnerability in DeFi isn't in the contract - it's in the calendar invite - what exactly are we auditing? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
