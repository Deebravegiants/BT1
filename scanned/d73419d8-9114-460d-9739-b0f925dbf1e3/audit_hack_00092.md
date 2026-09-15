# [C] Drift Protocol exploit: Credit: DLNews , Drift Protocol , DefiLlama , Mert , Vladimir S

## Summary
Severity: Critical
Target: Drift Protocol
Loss: $285,000,000
Published: 4/1/2025
Source: https://rekt.news/drift-protocol-rekt
Type: rekt-postmortem

## Details
## Drift Protocol - Rekt

 Thursday, April 9, 2026 Private Key Leak - Drift Protocol - DPRK 

 read this article also in : 

 Credit: DLNews , Drift Protocol , DefiLlama , Mert , Vladimir S. , Peckshield , Arkham Intelligence , Lookonchain , Unchained , CCN , CoinTelegraph , Andrew Hong , QuillAudits , wublock , ZachXBT , Specter , Temmy , TheBlock , molu , Fabiano , Omer Goldberg , Hayden Adams , Cube Exchange , BleepingComputer , Halborn , Tayvano , Ariel Givner , CoinDesk , The Hacker News , Mitchell Amador , TRM , Blockworks , Chainalysis , Patrick Collins 

 Mert saw it first . 

 On the morning of April 1st, the CEO of Helius, one of Solana's most critical infrastructure providers, posted a hedge that no one in DeFi ever wants to read : "Not 100% fully certain yet, but it seems drift might be getting exploited."

 Minutes earlier, he had already flagged the situation to Circle directly , urging someone to reach out "asap" over what he called a "high likelihood of a potentially large exploit."

 Circle did not respond publicly.

 Twenty minutes later, Vladimir S. had the numbers : Two addresses , roughly $200 million in SOL already moved , and a note that the exploit had been running quietly for a week . 

 PeckShield sent Drift a public nudge after that. 

 Drift's official acknowledgement came nearly an hour after the first public alarm.

 "We are observing unusual activity on the protocol. We are currently investigating. Please do not deposit funds into the protocol while we investigate. This is not an April Fools joke."

 That last line had to be written. April 1st meant the first wave of users who saw the warning assumed it was a bit.

 Shortly after that first acknowledgment, Drift confirmed an active attack , suspended deposits and withdrawals, and announced coordination with "multiple security firms, bridges, and exchanges." 

 They repeated the line again, " this is not an April Fools joke ", as if repetition might make people take it seriously this time.

 By then, Arkham Intelligence had tracked over $268 million moving from Drift's vault to an interim wallet .

 Attacker’s Address on Arkham: 

 98e28143-3e15-4e2a-8527-f30d4c7c11aa 

 The vault's balance had collapsed from $309 million to $41 million . Then lower. Currently sitting just south of $8 million .

 The attacker, meanwhile, was already converting to ETH . 

 If the first public warning came an hour before Drift confirmed anything, and the drain was already finished by then, what exactly was the monitoring infrastructure watching? 

## Not an Overnight Operation

 The attack didn't start on April 1st. It started on March 23rd. April 1st was just when it finished. 

 The attack had three moving parts , each one useless without the others, each one assembled in plain sight over the course of ten days. 

 Understanding how it worked means understanding all three, because this wasn't a hack. It was a setup.

 Part One: The Fake Token. 

 On March 12th , three weeks before the drain, the attacker created a token on Solana called the CarbonVote Token, CVT . 

 CVT token on Dex Screener: 

 dqcs7ezc6nc4ju6hcvvamkmnwzdxigtkggdjqpm4zgbl 

 They minted 750 million units for $1.19 , then seeded a Raydium liquidity pool with $500 .

 Then they wash-traded it between their own wallets , back and forth, day after day, building a price history that sat near $1 per token.

 The price was fed to Drift by an oracle the attacker themselves had deployed and controlled . 

 By the time the attack fired, CVT had a credible, weeks-long price record . The oracle wasn't fooled. It was theirs. 

 CVT mint address: 
 G84LEhbNMR1yYbHgHbnNYNSK8mpTKcazh5jcW5yMPQKo 

 $501.19 That was the seed money for a $285 million theft. 

 Part Two: The Durable Nonce. 

 Solana has a feature called a durable nonce. It lets users pre-sign a transaction and hold it, bypassing the normal short expiry window, for execution at any future point. It's a legitimate tool, built for multisig workflows and offline signing. 

 The attacker turned it into a time-delayed detonator. 

 On March 23rd, four durable nonce accounts were created . Two were controlled by the attacker. Two were linked to legitimate members of Drift's Security Council multisig.

 Multisig member nonce accounts: 
 45cZ5Fj97Va5Abipr6NN8Zf1BqZqWneSek1hU5cQRvhw 39JyWrdbVdRqjzw9yyEjxNtTbTKcTPLdtdCgbz7C7Aq8 

 Attacker-controlled nonce accounts: CZRBcHAvXU6TzzjGuG4rT98UuTR7PBUeSGPZRDW5mfYW 48cV6Mw5Y5afT8ofukvtFaMtrsCohHhsv8MfbdW8agh3 

 In the days following the nonce setup, Drift executed a planned Security Council migration , replacing four of five signers and lowering the signing threshold from 3-of-5 to 2-of-5 . 

 The attacker didn't miss a beat. Within days of the new multisig going live, they had already obtained a pre-signed nonce from one of the replacement signers . 

 New multisig member nonce account: 
 6UJbu9ut5VAsFYQFgPEa5xPfoyF5bB5oi4EknFPvu924 

 The multisig was seven days old. The attacker already had two of the five keys.

 Part Three: The Social Engineering. 

 What the on-chain record showed was the final act. The full picture took another week to emerge. 

 For the durable nonce setup to work, legitimate multisig signers had to pre-sign transactions they didn't fully understand. 

 Drift's own statement calls it "targeted social engineering or transaction misrepresentation." The signers approved something. They just didn't know what they were actually approving.

 One detail stands out. On March 25th, Drift hosted "Liquid Hours NYC" , a happy hour event during DAS NYC, co-sponsored with AWS and Failsafe .

 The attacker's first funding transactions arrived roughly twelve hours before that event started.

 Whether that timing means anything remains unconfirmed. 

 What is confirmed : the attacker funded the entire operation from Tornado Cash three weeks prior, 10 ETH bridged from Ethereum to Solana via LiFi and NEAR intents, then dispersed across wallets in the lead-up to April 1st. 

 Origin transaction: 0x14cd918f2c1ffcd9a96f9d2ccd1988469fd246a3ed4e3565d2fa5b5b91238ba1 

 One footnote worth noting: Neodyme's 2024 security audit of Drift explicitly reviewed the protocol's authority structure, including the admin's ability to initialize markets and update parameters.

 According to Vladimir S. who reviewed the report post-hack , that architecture was not classified as a critical, medium, or low severity issue. It appears to have been treated as an acceptable assumption within the protocol's trust model.

 No audit catches a compromised private key. But someone had looked directly at this door, decided it was fine, and moved on. 

 If the attack was never going to show up in a code review, what governance structure could have stopped it before two signatures handed over $285 million? 

## 128 Seconds

 The setup took patience. The execution took less time than it takes to read this paragraph. 

 One minute after Drift executed a routine test withdrawal from its own insurance fund on the afternoon of April 1st, the pre-signed nonce transactions fired. 

 Two transactions. Four slots apart. Admin transferred.

 Create + approve malicious admin transfer: 2HvMSgDEfKhNryYZKhjowrBY55rUx5MWtcWkG9hqxZCFBaTiahPwfynP1dxBSRk9s5UTVc8LFeS4Btvkm9pc2C4H 

 Approve + execute malicious admin transfer: 4BKBmAJn6TdsENij7CsVbyMVLJU1tX27nfrMM1zgKv1bs2KJy6Am2NqdA3nJm4g9C6eC64UAf5sNs974ygB9RsN1 

 With that, Drift's State account had a new owner .

 Attacker owned Drift's State account: 5zpq7DvB6UdFFvpmBPspGPNfUGoBRRCE2HHg5u3gxcsN 

 In the same slot , whoever now controlled that key acted immediately. A new collateral market was created for CVT with maximal permissive parameters, and updateWithdrawGuardThreshold() was called across five markets, raising withdrawal caps to 500,000,000,000,000 across the board . Every safety limit, effectively gone. 

 What followed took 128 seconds . 

 At the 25-second mark, the attacker initialized a Drift user account under their own key. Three seconds later, they deposited 500 million CVT into spot market index 63 , the collateral market the compromised admin key had created moments earlier with permissive parameters.

 The deposit cost them essentially nothing . CVT had negligible real market value, but the permissive collateral weights set by the attacker allowed them to borrow against it as if it were worth far more. 

 CVT deposit transaction: 5V72ZK1WejP5Mh3uryEy6BZCV6ukSAnZBFSvHTqfD4NS38xKJUuh4RV5F8D4tDbgMsB2dcTJyZf7hLxH34nCRHRE 

 Then the withdrawals began. Starting at the 30-second mark, 18 tokens drained across multiple vaults : 

 JLP: 42.72M tokens - $159,350,000 

 USDC: 71.42M USDC - $71,420,000 

 cbBTC: ~164.35 BTC - $11,290,000 

 USDT: 5.65M USDT - $5,650,000 

 USDS: 5.25M USDS - $5,250,000 

 WETH: 2,200.59 WETH - $4,690,000 

 dSOL: 45,292.21 dSOL - $4,470,000 

 WBTC: 63.47 WBTC - $4,360,000 

 Fartcoin: 23.37M - $4,110,000 

 JitoSOL: 33,976.51 JitoSOL - $3,600,000 

 syrupUSDC: 2.87M - $3,320,000 

 INF: 21,241.62 - $2,500,000 

 mSOL: 17,418.92 mSOL - $1,990,000 

 bSOL: 9,474.33 bSOL - $1,020,000 

 EURC: 583,980.69 - $677,420 

 zBTC: 8.61 - $586,790 

 USDY: 477,375.42 - $539,430 

 JUP: 2.62M - $431,440 

 Confirmed total : $285.26M

 The JLP vault went first , $159 million, the single largest position. cbBTC was left with ~ .16 of a bitcoin. By the time the final withdrawal closed at the 128-second mark , the vaults were stripped significantly.

 Executor wallet (deposit + withdrawal cascade): 55udxhScWQxM7cC9d1NPBQoEDC7B38w81EWKPZsM7ZCW 

 Primary receiving wallet (stolen tokens): HkGz4KmoZ7Zmk7HN6ndJ31UJ1qZ2qgwQxgVqQwovpZES 

 Secondary consolidation wallet: 
 8ubo4HbWJHKyFJYJc2Gh74dxCP7bN7Fu2Pi13KZ9rGxw 

 From there, the exit was methodical. Some stolen assets were routed through Jupiter on Solana, swapped into USDC, WSOL, WBTC, and WETH, then bridged to Ethereum via Circle's Cross-Chain Transfer Protocol across more than 100 transactions over six hours .

 SOL took a different route : Bridged to Ethereum via Chainflip, fragmenting the trail across platforms.

 Chainflip destination address: 
 0xd91a122b585bc588c9a48d0995ee0d7b4f8ab7dd 

 On Ethereum, the attacker consolidated stolen funds into ETH across four receiving addresses .

 Attacker EOAs on Ethereum: 
 0xD3FEEd5DA83D8e8c449d6CB96ff1eb06ED1cF6C7 0xAa843eD65C1f061F111B5289169731351c5e57C1 0xbDdAE987FEe930910fCC5aa403D5688fB440561B 0x0FE3b6908318B1F630daa5B31B49a15fC5F6B674 

 Three weeks of preparation. One minute of admin access. A hundred and twenty-eight seconds to empty the vaults. Then six hours of bridging, in broad daylight, during US business hours, while the stolen USDC moved freely through Circle's own infrastructure.

 Nobody stopped it. 

 Over $230 million in USDC crossed Circle's own bridge in plain sight for six hours, so why did it take a public callout on Twitter to make anyone ask where Circle was? 

## While You Were Sleeping

 Six hours. That's how long $230 million in stolen USDC spent moving through Circle's own Cross-Chain Transfer Protocol, burning on Solana, minting on Ethereum, across more than 100 transactions, during US business hours, on a Tuesday afternoon. 

 Circle did not freeze a dollar of it. 

 ZachXBT put it plainly : "Circle was asleep while many millions of USDC was swapped via CCTP from Solana to Ethereum for hours from the 9 figure Drift hack during US hours. Value was moved and nothing was done yet again."

 Onchain Investigator Specter added a detail that made the silence harder to excuse. The attacker had parked the stolen USDC across multiple wallets for one to three hours before moving it , sitting on it, waiting.

 They also made a deliberate choice not to convert to USDT during the bridging process . They chose USDC specifically, and they held it patiently, apparently confident that Circle would not act . 

 They were right. 

 What made the inaction land differently was the timing. Nine days earlier, Circle had frozen USDC across 16 unrelated business hot wallets , exchanges, casinos, forex firms, a DFINITY bridge contract with thousands of users behind it, as part of a sealed US civil lawsuit. No public explanation. No advance warning. 

 One wallet, belonging to Goated.com, was quietly unfrozen three days later. Most remained locked as of April 2nd. 

 ZachXBT had already called the freeze "incompetent" , noting the wallets were still being slowly unfrozen.

 Now, nine days later, the same infrastructure watched a confirmed nine-figure theft move through it in real time. 

 Circle has not publicly responded to the criticism. 

 Are they just being Circle Jerks?

 molu framed the structural problem cleanly : "Circle could freeze it. But they're not required to."

 That's the gap, between capability and obligation, that the Drift hack forced into the open. Proposed regulatory frameworks like the GENIUS Act could eventually change that calculus , but as of April 1st, no rule required Circle to move. So they didn't.

 The USDC debate was the loudest secondary story, but it wasn't the only fallout.

 At least 20 protocols reported disruptions, pauses, or losses , with several pausing deposits, withdrawals, or key features while assessing exposure.

 The day after the exploit, a multisig comparison began making the rounds .[

 Drift's 2/5 multisig with zero timelock meant any two signers could authorize instant, irreversible admin-level changes, no delay, no review window, no circuit breaker. 

 Fabiano, mapped out where Drift sat relative to its peers : 

 Jupiter Lend: 4/7 multisig, 12 hour timelock 

 Kamino: 5/10 multisig, 12 hour timelock 

 Solstice: 3/5 multisig, 1 day timelock 

 Loopscale: 3/5 multisig, not listed 

 Exponent: 2/3 multisig, not listed 

 Drift: 2/5 multisig, no timelock 

 Chaos Labs founder Omer Goldberg laid out the structural failure: * "The protocol's signer key had full control over market creation, oracle assignment, withdrawal limits. There was no time lock, no multisig, and no delays." The full sequence, he noted, took less than 15 seconds .

 Uniswap founder Hayden Adams went further : "We have to stop letting centralized things call themselves DeFi. Admin key can drain all funds? CeFi. Otherwise DeFi means nothing and it’s brand is destroyed."

 Cube Exchange put the longer arc into words : "The threat model FTX made obvious, custodial risk, concentrated authority, opaque internal controls, did not disappear when the industry switched from CeFi to DeFi. It just moved from a CEO's discretion to an admin key's permissions."

 Every chain is only as strong as its weakest link. At Drift, that link was two signatures and no timelock. 

 Was this an acceptable security model for a protocol that lost $285 million in user funds? 

## The Long Con

 Everything we knew about this attack last week was wrong, not in the details, but in the scale. 

 Ten days of setup . That's what the on-chain record showed. 

 Initial nonce setup March 23rd , a multisig migration days later , execution on April 1st . Tidy. Traceable. A ten-day window that felt like a long time for a crypto exploit.

 Except, the set up wasn't ten days. It was six months.

 On April 4th, Drift published its Incident Background Update . What it described wasn't a hack. It was a structured intelligence operation, the kind that requires organizational backing, significant resources, and the patience of people who are very, very good at being someone else.

 It started at a conference. Around October 2025, a group posing as a quantitative trading firm approached Drift contributors at a major crypto event, expressing interest in integrating with the protocol. 

 They were technically fluent . They had verifiable professional backgrounds. They knew how Drift worked. They set up a Telegram group upon the first meeting and stayed in it. 

 Over the following months, they kept showing up , at conferences, at industry events, across multiple countries. They weren't strangers sending cold DMs. They were colleagues. People Drift contributors had met in person, worked through sessions with, built what felt like a normal professional relationship with over nearly half a year .

 Between December 2025 and January 2026 , the group went further. They onboarded an Ecosystem Vault on Drift , which required filling out strategy documentation and engaging with contributors directly.

 They deposited over $1 million of their own capital . They participated in working sessions. They asked detailed, informed product questions. They did everything a legitimate trading firm integrating with a DeFi protocol would do.

 By February and March 2026, these were not strangers , they were people Drift contributors had worked with and met in person. 

 Then came the tools. As integration conversations deepened, the group began sharing links, repositories, and applications , described as frontend deployments for their vault, a wallet product still in testing. 

 One contributor may have cloned a code repository the group shared. Another may have downloaded a TestFlight application the group presented as their wallet product. Drift has not confirmed with certainty which vector succeeded , both remain under active forensic investigation.

 For the repository vector, Drift pointed to a known vulnerability in VSCode and Cursor , two of the most widely used code editors in software development, that the security community had been flagging since late 2025.

 The flaw required no clicks, no permissions dialog, no warning of any kind. Simply opening a file or folder was enough to silently execute arbitrary code on the contributor's device. 

 Once inside those devices, the attackers had what they needed: Access to the signing workflows that would let them obtain multisig pre-approvals. The durable nonce accounts, the pre-signed transactions, the whole March 23rd setup , all of it traces back to this. The on-chain story was chapter four of a six-chapter operation. 

 Immediately after the April 1st drain, the group scrubbed everything. Telegram chats deleted. Malicious software wiped. The trading firm that had spent six months building a relationship with Drift contributors simply ceased to exist. 

 Drift, working with the SEAL 911 security team , assessed with medium-high confidence that the operation was carried out by UNC4736, a North Korean state-affiliated group also tracked as AppleJeus or Citrine Sleet .

 The connection rests on both on-chain fund flows tracing back to the actors behind the October 2024 Radiant Capital hack , and operational overlaps between personas used in this campaign and known DPRK-linked activity.

 One detail Drift was careful to stress : The individuals who appeared in person at conferences were not North Korean nationals.

 DPRK operations at this level deploy third-party intermediaries , people with fully constructed identities, employment histories, public-facing credentials, and professional networks built specifically to survive due diligence. 

 Non-Koreans, working for Koreans, running a con that took six months to pay off. 

 The playbook is not new. In October 2024, Radiant Capital lost approximately $53 million after attackers posed as an ex-contractor and delivered malware through a ZIP file shared on Telegram.

 The Drift operation was the same logic at roughly six times the scale and six times the patience.

 MetaMask developer and security researcher Taylor Monahan didn't soften the wider implication : "Lots of DPRK IT workers built the protocols you know and love, all the way back to DeFi summer." 

 She listed at least 40 DeFi platforms she believes have been infiltrated by North Korean IT workers at some stage . "The seven years of blockchain dev experience on their resume is not a lie," she added , then warned that the depth of the Drift operation " makes me think they already have multiple other teams on lock. " 

 ZachXBT drew a line between the threat types : "Threats via job postings, LinkedIn, email, Zoom, or interviews are basic and in no way sophisticated, the only thing about it is they're relentless. If you or your team still falls for them in 2026, you're very likely negligent."

 IP and Corporate Attorney Ariel Givner agreed , and went further: “I can’t help but think we’re dealing with a civil negligence issue.”

 Givner continued : "In plain terms, they failed their basic duty to protect the money they were managing. You can’t just shrug, say “state hackers did it,” and leave users holding the bag. People trusted Drift with their funds… not with playing risky games against pro attackers.”

 With the Drift exploit attributed to DPRK by Elliptic , TRM Labs , and Drift's own investigation , it would be the eighteenth such operation Elliptic has tracked in 2026 alone , pushing North Korean crypto theft past $300 million for the year, before April was over. 

 If it took six months to rob Drift, how long have they already been inside the next one? 

 Nobody broke Drift's code. They broke its people, and they had six months to do it properly. 

 $285 million left a protocol that looked bulletproof on paper - audited code, a seat at the Solana DeFi table. But, none of it mattered. 

 Not because a bug slipped through. Because what appears to be a state-sponsored intelligence operation with real capital, real identities, and real patience decided Drift was worth six months of their time. They were right.

 The attacker funded this entire operation with 10 ETH from Tornado Cash . What they walked away with was the largest DeFi exploit of 2026, so far…

 At that return on investment, the only question is why they didn't start sooner.

 Drift sent on-chain messages to the four wallets holding stolen funds , asking them to reach out through Blockscan. 

 No compensation plan has been published. 

 Drift is working with Asymmetric Research and OtterSec on a coordinated recovery plan and will participate in the Solana Foundation's STRIDE program .

 On April 9th, Drift posted an interim update : “We recognize the impact this has had across our users and the builders who have integrated with us - many of whom rely on Drift as core infrastructure. We’re actively working on next steps and will share more once details are finalized.”

 Immunefi's data is unsparing : 83% of native tokens from hacked protocols never recover to pre-hack prices. Not because the technology fails, but because trust, once broken at this scale, doesn't have a patch.

 Drift had already lost $1 billion in TVL since its October peak before the attack landed. It has less runway than most and further to fall. 

 Bybit lost $1.5 billion the same way. 

 Ronin lost $625 million the same way.

 Radiant Capital lost approximately $53 million as a rehearsal for this .

 North Korean hackers have stolen over $6.75 billion in crypto , and the pace is accelerating, not because the targets are getting easier, but because the operations are getting longer, more patient, and harder to see coming until they're already done.

 Private key compromises accounted for 88% of all stolen crypto in Q1 2025 . Social engineering is the entry point for almost every major theft in this industry. The industry has known this for years. It responds to each new incident with the same cycle: shock, postmortem, a few weeks of governance discussion, then back to building as if the next team won't be targeted the same way. 

 Patrick Collins called it the scariest hack of 2026 , scarier than Bybit, despite being a fraction of the size. Not because of the technical exploit. 

 Because of what it proved : "Meeting somebody in person isn't going to be the obstacle we historically thought it would be."

 If the industry's last line of defense against state-sponsored infiltration was a handshake and a conference badge, that line is already gone.

 Somewhere out there, another protocol is running a 2-of-5 multisig with no timelock. Another contributor just accepted a GitHub invite from a technically fluent stranger they met at a conference. Another TestFlight link is sitting in a Telegram chat, waiting to be opened.

 North Korea didn't find a hole in DeFi's code. They found a hole in DeFi's culture. 

 How many more billion-dollar lessons does it take before that changes? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
