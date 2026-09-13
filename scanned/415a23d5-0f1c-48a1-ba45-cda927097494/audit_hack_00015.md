# [C] AlexLab - Rekt II exploit: Lightning struck twice at AlexLab, and this time it brought friends

## Summary
Severity: Critical
Target: AlexLab - Rekt II
Loss: $16,180,000
Published: 6/6/2025
Source: https://rekt.news/alexlab-rekt2
Type: rekt-postmortem

## Details
## AlexLab - Rekt II

 Monday, June 9, 2025 AlexLab - Rekt - Defi 

 read this article also in : 

 Lightning struck twice at AlexLab, and this time it brought friends. 

 Just over a year after losing $4.3 million to a compromised private key , Bitcoin's self-proclaimed "finance layer" got stripped down to the studs again. 

 This time, a cunning attacker exploited AlexLab's self-listing verification logic, turning their permissionless token listing feature into a $16+ million liquidity siphon on June 6th.

 While AlexLab scrambled to blame Stacks blockchain's "inability to detect failed transactions," someone was busy proving that the real failure was much closer to home.

 Armed with nothing but fake tokens and a deep understanding of AlexLab's architectural blind spots, the exploiter drained multiple asset pools in a single transaction, walking away with millions in STX, aBTC, sBTC, ALEX tokens, and stablecoins. 

 When your protocol gets exploited twice in 13 months using completely different attack vectors, are you building DeFi infrastructure or just expensive honeypots? 

 Credit: Reubs BTC , Crusader , AlexLab , Nolan-Exvul 
 Friday morning, June 6th, while some of the world was still in shock about Trump and Musk’s alleged public break up, Twitter user Reubs BTC was sounding alarms that would wake up more than just early traders. 

 "Hold on tight friends. Looks like ALEXLabBTC has been hacked."

 Within minutes, Crusader on Twitter announced the carnage : "62 $BTC, 8M $STX, 119m $Alex, $1.7M USDT. Not again."

 AlexLab's damage control kicked in shortly after with their trademark understatement: "We are aware of the malicious activities at ALEX."

 Platform activities were suspended faster than you could say "exit liquidity," while the team promised a full post-mortem "as soon as possible." 

 Two hours of radio silence later, AlexLab finally admitted the obvious : they'd been exploited. 

 Their explanation read like a polished exercise in strategic blame assignment: "The attacker exploited a flaw in verification logic in the self-listing function by referencing a failed transaction, allowing a malicious token to bypass checks and transfer funds from liquidity pools."

 But here's where it gets spicy. AlexLab immediately pointed fingers at Stacks itself , claiming "the core issue stems from a current on-chain limitation, specifically the inability to reliably detect failed transactions on Stacks."

 Translation: "It's not our fault, it's the blockchain's fault." 

 A couple of hours later, AlexLab had tallied their official damage report : $8,373,227 across STX, sBTC, USDC/USDT, and WBTC.

 They promised "full reimbursement in USDC" using their foundation treasury, complete with a slick compensation timeline and claim process.

 One small problem: the actual transaction data tells a very different story. 

 What does the blockchain tell us? 

## The Chain Doesn’t Lie

 The blockchain reveals what really happened - and it's uglier than AlexLab's sanitized press release. 

 Vault Stolen From: 

 SP102V8P0F7JX67ARQ77WEA3D3CFB5XW39REDT0AM.amm-vault-v2-01 

 Attacker’s Address: 
 SP2VCNXGRZCBTP8E9MQ6DJPFVXRBPWBN63FE06A1M 

 Stolen funds transaction: 
 0xe8b2ac705dcbb35d487a4efd7a0fe384bbad1d1d97ea970410ad82a3cd0d9daf 

 Here's what the attacker actually walked away with: 

 8,403,867 STX ($5.54M)

 50.74 aBTC ($5.43M)

 12.76 sBTC ($1.35M)

 119,419,656 ALEX tokens ($2.12M)

 1,748,327 sUSDT ($1.74M)

 Total real damage: Over $16.18 million. 

 That's nearly double what AlexLab officially reported.

 Either their accounting department needs new calculators, or someone's been playing fast and loose with the truth. 

 But how do you turn fake tokens into $16 million of real money? 

## How the Magic Trick Worked

 AlexLab built a vault system with permission controls. Someone figured out how to become the vault. 

 Step one: Deploy a malicious token called "ssl-labubu-672d3" - because naming your scam token after a cartoon character is peak 2025 energy.

 But this wasn't just any token - it contained a fake transfer function designed to drain AlexLab's vault. 

 The exploit had nothing to do with AlexLab's claimed "inability to reliably detect failed transactions on Stacks" - it was a systematic vault heist using AlexLab's own permission system against them.

 While AlexLab pointed fingers at blockchain limitations , the real vulnerability was their lax vault access controls and misuse of smart contract functions.

 Security researcher Nolan from Exvul broke down the real attack vector , revealing how the attacker weaponized AlexLab's vault permissions rather than exploiting any Stacks blockchain limitation. 

 Step two: Create a legitimate Labubu/STX pool, which automatically triggers AlexLab's set-approved-token function and grants vault permissions.

 Step three: Enable farming by flipping the set-enable-farming flag to 9, unlocking the malicious token's transfer abilities.

 Step four: Execute a single swap-x-for-y call. The real magic happens in the vault contract.

 When AlexLab's system calls the malicious token's transfer function using as-contract, it changes the transaction context - making the vault itself appear as the sender rather than the attacker. 

 With vault-level permissions, the fake token's transfer function systematically drained every asset: STX, aBTC, sBTC, ALEX tokens, and sUSDT - all transferred directly to the attacker's address.

 One transaction and the entire vault was drained. Mission accomplished.

 Someone either spent serious time studying AlexLab's code, or they had a front-row seat to its development. 

 But wait - didn't AlexLab just get audited? 

 AlexLab had recently invested in comprehensive security reviews from two firms - Clarity Alliance and CoinFabrik - both delivering audits in May.

 Here's the catch: they were auditing AlexLab's upcoming DAMM (Discrete Automated Market Maker) system, scheduled for July launch.

 The live vault infrastructure that actually got exploited? Outside the audit scope.

 The security firms did exactly what they were contracted to do - audit the code they were given. 

 When your future product gets bulletproof security while your live system gets drained, who's really setting the priorities? 

 Two exploits, thirteen months, same protocol - different playbook entirely. 

 First time around, AlexLab lost $4.3 million to a compromised private key. 

 This time, they lost almost 4 times that amount to someone who simply understood their code better than they did.

 While AlexLab scrambles to blame Stacks blockchain limitations, the attacker already cashed out with cartoon-named tokens and a masterclass in vault exploitation.

 Their compensation promises sound generous until you realize they're offering to cover $8 million when the real damage hits $16 million.

 Meanwhile, users who trusted a protocol fresh from two security audits are learning that smart contract reviews apparently don't cover the smart contracts that actually matter.

 AlexLab survived their first rekt story, but lightning striking twice suggests this isn't bad luck - it's bad architecture. 

 If your DeFi protocol gets exploited twice using completely different attack vectors, are you really building financial infrastructure, or just running an expensive bug bounty program for hackers? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
