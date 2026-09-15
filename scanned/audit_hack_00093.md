# [H] DxSale exploit: Nine months of patience, one admin key and $7.3 million gone

## Summary
Severity: High
Target: DxSale
Loss: $7,300,000
Published: 5/27/2026
Source: https://rekt.news/dxsale-rekt
Type: rekt-postmortem

## Details
## DxSale - Rekt

 Tuesday, June 2, 2026 DxSale - Admin Privileges - Rekt 

 read this article also in : 

 Nine months of patience, one admin key and $7.3 million gone . 

 Nobody broke DxSale's code. The code was never the problem. 

 A 2021 locker contract - unmaintained, unmonitored, still holding millions in locked LP tokens from projects most of crypto had long forgotten - was quietly handed to an attacker by whoever controlled the original owner key.

 That ownership transfer had been obscured through 80+ successive wallet hops to bury the trail.

 From that moment, the drain was inevitable. Only the timing was left to decide.

 On May 27, 2026, the attacker decided. 

 Using owner privileges and EIP-7702 batch delegation , they unlocked and drained more than 1,400 liquidity pools on BNB Chain in a single coordinated flow . Fees were set to zero. 

 Every LP token that projects had trusted DxSale to hold - secured, immutable, protected - became a withdrawable balance.

 Drained funds were then routed through multiple wallets, dispersed across Binance deposit addresses , before most of the affected projects knew anything had happened.

 DxSale's only public response was a tweet posted the following morning : "We're aware of a recent exploit and liquidity drain. Investigation is underway. Stay tuned for updates."

 No transaction hashes, no affected contract list, no acknowledgment of the $15.5M still sitting in compromised lockers.

 Two more locker contracts, 0x81E0eF68 and 0x2D045410 , had their ownerships transferred to the same attacker address and remain compromised. 

 When a platform built entirely around the promise of locked liquidity can be emptied by whoever holds one key, what exactly were those locks protecting? 

 Credit: Peckshield , GoPlus Security , DxSale , Tahax , Alaoui Capital , ExVul , eyeonchains , SlowMist , Decurity , DappRadar , SEC , SafeMoon 
 Tahax fired first in the early hours of May 28th , and then waited nearly fifteen hours for anyone else to notice. 

 Tahax had mapped the full skeleton of the attack before most of crypto had registered it was happening: The ownership transfer , the 80-hop obfuscation chain , the 269-day gap between when the contract changed hands and when the drain began.

 Tahax flagged that the exploiter wallet was freshly created and seeded through Bybit , alleged that a backdoor had been left in the contract without any public migration announcement , and assessed that tracing was already deeply complicated by the time the alert went out.

 The post landed. The reaction did not come in a timely manner either.

 GoPlus Security broke the silence nearly fifteen hours later , publishing the most operationally detailed alert of the incident - a full IOC list, the attack flow broken into steps, estimated values across all four affected locker contracts, and a direct recommendation for affected projects to withdraw immediately. 

 GoPlus put the primary drain at $7.3M and flagged that three additional locker contracts , whose ownership had also been transferred to the same attacker address, held an estimated $15.5M still at risk . 

 Alaoui Capital picked up the thread in the early hours of May 29 : "DxSale got cooked for $7.3M on BNB Chain," they wrote, walking through the basics - the old 2021 locker contract, the admin key abuse, the hidden backdoor - before landing on what everyone else was also noticing , "Team still hasn't responded, will be watching closely."

 DxSale finally appeared the morning of May 29 , more than 24 hours after Tahax's first alert.

 The post read : "We're aware of a recent exploit and liquidity drain. Investigation is underway. Stay tuned for updates."

 No transaction hashes, no affected contract list, no acknowledgment of the $15.5M still sitting in compromised lockers. 

 ExVul posted technical analysis later that day, followed by PeckShield , who put the clearest dollar figure on the fund movement, 2,958 BNB (~$1.87M) traced moving to two main wallets before being deposited into multiple Binance deposit addresses. 

 eyeonchains added the most consequential piece of context , surfacing screenshots from August 2025 showing someone operating a paid unlock service directly through DxSale's own Telegram channel.

 The operator claimed to have insider contacts within the DxSale team who could unlock old LPs from projects launched before late 2021 , taking a 20% cut of recovered funds as payment.

 By their own account, they had already recovered $200K and been paid out $100K before the screenshots were taken . 

 The only requirement was that someone from the original project team still had access to the wallet used to raise funds on DxSale.

 eyeonchains concluded that after the exploit, it felt like the backdoor may have existed for years , raising the possibility that it came from someone with insider-level access, potentially a former DxSale team member who already knew how those LPs could be unlocked all along.

 SlowMist logged the incident in their hacked database under a classification that required no editorial judgment: Private Key Leakage.

 The chain had the whole story within hours of the drain. The team that built the platform said almost nothing. 

 When the most detailed public accounting of what happened comes from third-party researchers and a 24-hour-delayed tweet, what does that tell you about who was actually watching? 

## Keys To Everything

 DxSale's locker contract was deployed in 2021 on BNB Chain during the peak of the memecoin boom . Hundreds of token launches used it to lock LP tokens, a trust signal to investors that developers couldn't immediately rug pull by removing liquidity. 

 The platform processed thousands of locks across that cycle and then, like much of that era's infrastructure, quietly receded from active development while the assets it held did not. 

 That's the first problem. A contract holding tens of millions of dollars in LP tokens from projects across the 2021 launch cycle had received no audit updates, no security monitoring, and no migration path in the years since.

 The original owners had, in many cases, long since moved on . The contract just sat there - loaded, unguarded, and governed by a single privileged key.

 That key is the second problem, and the more fundamental one.

 The locker contract inherited Solidity's standard Ownable pattern , which includes a transferOwnership function that does exactly what it sounds like, transfers full administrative control to any address, at any time, with no delay, no secondary approval, and no on-chain announcement required . 

 Whoever owned the key owned the contract. Whoever owned the contract could trigger LP token transfers out of the locker directly , bypassing every time-based restriction that token projects believed was protecting their locked liquidity. 

 The locks were never immutable. They were administrative settings. The difference between "locked" and "withdrawable" was whoever held the owner key - and at some point, that person handed it to someone they shouldn't have, or became that person themselves.

 Whether the original owner key was externally compromised ,or whether whoever held it may have acted from the inside , remains publicly unanswered. The mechanism is clear. The motive is not.

 SlowMist's classification of "Private Key Leakage" is the most precise framing available : The attack used legitimate administrative functions, wielded by someone who had no business wielding them.

 On May 26, 2026 , the original owner called transferOwnership on the primary locker contract, passing full control to the attacker address. 

 The same original owner had already transferred ownership of two additional locker contracts to that same destination. On-chain confirmation of this transaction predates the drain by two days, the attacker had the keys, funded by Bybit , and waited. 

 Original Owner Address: 
 0x47BAcf935066b802EAA0067eC14AB035B24eB78b 

 Attacker Address: 
 0xC4574DDEF299e7E563971e200433e592EeaaFA69 

 EIP-7702 , the batch delegation mechanism introduced in the Pectra upgrade, provided the infrastructure to hit more than 1,400 pools efficiently .

 DxSale's May 30 statement attributed the exploit to "BSC's recent atomic tx feature" , a reference to EIP-7702's batch transaction capability, while making no mention of the ownership transfer that gave the attacker administrative control months before the drain.

 This wasn't the first time someone had pointed at this exact vulnerability class in DxSale's architecture. 

 In June 2023, at the time operating under the DxApps rebrand , before reverting to the DxSale name, security firm Decurity disclosed a critical bug in the same locker contract that could have allowed an attacker to drain approximately $5.2 million in locked LP tokens . 

 The fix was to raise the locking fees high enough to make exploitation economically unattractive - a deterrent, not a structural repair.

 Decurity noted that the solution left one avenue fully intact : The contract owners themselves could still drain the funds whenever they chose. The developers acknowledged this and explicitly decided to leave it as is.

 That observation aged poorly.

 If the root cause is a single unprotected owner key with unchecked authority over millions in locked assets, the follow-up question isn't technical, it's organizational. 

 Who held that key, why did they transfer it, and where have they been since the drain? 

## Follow the BNB

 The attacker's wallet was seeded with 104 BNB , roughly $67,000, from Bybit approximately 20 hours before the main drain began. 

 A calculated operational move: load the gas, confirm the infrastructure, then execute. 

 The wallet itself was freshly created, purpose-built for this .

 Attacker Wallet: 
 0xC4574DDEF299e7E563971e200433e592EeaaFA69 

 EIP-7702 delegator contracts deployed as part of the execution infrastructure: 
 0x74Ad1Ef17Fbb3e494c31c72F7ec730A27FEf0310 0x996521B5Bb2bbF34764d89932f0Ea206e6A3A388 0xd6c7d6b19b9c05E8591542a13D297047C362d268 0xA0795423A2647eC750fEA5cAD3B709cFe7C814be 0xc2efbD94aeDFf1555b97ddCb216646DFC01e4718 

 From there, extracted funds were funneled through a chain of aggregation and relay wallets before reaching Binance deposit addresses. 

 Intermediate aggregation and relay wallets: 0x47F80D09d1Bd0BB675ac627BDC1d1244731F66bf 0xF19acAD8EDCd733A8bF9175C93da9AB660afC747 0xb71c1C2A0cD7A88f1317f9A996e4d121E7db5E92 0x4c5ee9703653C8e7725C65593bff372655e0453C 

 Key on-chain transactions are as follows… 

 Ownership Transfer - Primary Locker: 0x23e331a81e496890c8f6147a672c6bc45cc2d2dd17547e72713b6ee070b38d41 

 Ownership Transfer Locker 2: 0xeb24afe9d1097f16bc7fe76a471f6c0dc8d504c67342afdeb01a9f97c5fb57a0 

 Ownership Transfer Locker 3: 0xdfda83a5af154fdf7768ec2e1722bb1be112f4fe7ecb2a0688381983d2f819f3 

 EIP-7702 Delegation Setup Example: 0xe6d29d066a9dab541bc5d2ded34696513e777ca79e615e71f036c8bb6ac6ac06 

 Primary LP Token Drain Example: 0xb107f19af1a8ff90d19cbb40d935f8be5d79f5fb9b497824e4ed28b9e7555fe9 

 Liquidity Removal Example: 0xb0ee7388ab64f6bafc3b8734ccb7c7dc2bb409723d57c98dc132c8851e2c4459 

 PeckShield traced funds to multiple Binance deposit addresses .

 GoPlus Security recommended that affected security teams submit on-chain evidence and request freezing of attacker-related accounts, noting that the Bybit seed funding provides a KYC entry point .

 Whether either exchange has acted on those requests has not been confirmed publicly.

 Direct verification of the three locker contracts as of publication are as follows… 

 Primary locker contract that was fully drained: 

 0xEb3a9C56d963b971d320f889bE2fb8B59853e449 

 Two additional locker contracts remain compromised and loaded: 
 0x81E0eF68e103Ee65002d3Cf766240eD1c070334d (confirmed $13.28M) 0x2D045410f002A95EFcEE67759A92518fA3FcE677 (confirmed $2.84M)

 Both contracts had ownership transferred to the attacker by the same original owner address: 

 0x47BAcf935066b802EAA0067eC14AB035B24eB78b 

 Neither has been drained at time of writing.

 Total confirmed remaining exposure : $15.5 million.

 The $7.3M is the confirmed damage from the primary locker. The primary contract is verified empty.

 The $15.5 million in the two remaining contracts is unresolved , the attacker holds the keys to both and has made no move on them yet. 

 Two contracts holding $15.5 million remain compromised, the attacker still holds the keys, and DxSale has said nothing about either, so what exactly are we not being told?" 

## Five Hundred Dollars

 The v1 locker contract deployed in 2021 was never upgraded or replaced, it simply continued holding LP tokens from that era while the platform moved on. 

 DxSale's v3.3 release in March 2022 introduced a completely revamped locker architecture. The v1 contract that was drained is the original - abandoned in place, still loaded. 

 DxSale broke their silence on May 30 with a second statement : "We've isolated the issue to v1 lockers (launched in 2021). The exploit stems from BSC's recent atomic tx feature. Rest assured: 100% of lockers (v2+) are safe & Certik-audited."

 Three things are notable about this statement.

 First, attributing the exploit to BSC's atomic transaction feature, EIP-7702, is a deflection. EIP-7702 enabled the scale of the drain; the unprotected owner key enabled the attack.

 Second, confirming that only v1 lockers were affected says nothing about the $15.5 million still sitting in two additional compromised locker contracts . 

 Third, citing a CertiK audit on v2+ contracts is cold comfort for the 1,400+ projects whose v1 liquidity is already gone . There is still no post-mortem, no compensation plan, and no list of affected projects. 

 The silence on those questions is its own data point.

 DxSale has documented ties to SafeMoon , one of the most notorious projects of the 2021 BNB Chain cycle.

 SafeMoon conducted its fair launch on DxSale and locked its LP on DxLocker for four years , the same locker infrastructure at the center of this exploit.

 SafeMoon's team members were later criminally charged by the SEC for fraud and unregistered offering of crypto securities . 

 GoPlus noted the historical connection between the two platforms as part of their incident analysis. 

 The on-chain evidence raises questions about the nature of this exploit. Ownership of the primary locker contract was transferred 269 days before the drain , a timeline inconsistent with an opportunistic external attacker who stumbled across a vulnerability.

 The multi-day execution, the controlled pacing, the pre-loaded gas wallet, the 80-hop obfuscation chain built before the drain, none of it reads as improvised.

 Whether that reflects insider knowledge or a long-planned external operation remains unconfirmed.

 Then there is the Telegram evidence. eyeonchains surfaced posts from August 2025 , almost nine months before the drain, in which someone was openly marketing an insider-connected service to unlock legacy DxSale LP positions. 

 With the condition : Someone from the original project team still had to control the wallet used to raise funds on DxSale. The fee was 20% of whatever was recovered. 

 Whether the operators of that service and the operators of this exploit are the same people remains unconfirmed.

 What is confirmed is that someone with knowledge of how those locks could be undone was monetizing that knowledge publicly, nearly a year before anyone got around to using it at scale.

 This brings us back to Decurity . In June 2023, three years before the drain, they disclosed a critical bug in the same contract, were paid $500 for their trouble , and documented explicitly that the fee-based fix left the owner key exposure fully intact.

 The contract owners could still drain the funds whenever they chose. The developers acknowledged this and decided to leave it as is. 

 Three years later, whoever held the owner key used it. 

 The question of whether this was an external attacker who obtained the key through compromise, or someone who was always on the inside, remains open. DxSale has offered nothing that would help answer it.

 The original owner address that called transferOwnership is on-chain and visible to anyone . Who controls it is not.

 What's left is a protocol whose product was trust, whose architecture undermined it, whose warnings went unheeded, and whose team has gone quiet at precisely the moment their users needed them most. 

 Is that negligence, or something worse? 

 DxSale was built to solve a specific problem : Users being rugged. 

 Their own documentation describes the platform launched specifically to address that , becoming the first decentralized launchpad with locked liquidity. 

 That promise is now $7.3 million lighter.

 The platform's entire value proposition rested on that promise - that liquidity, once locked, stayed locked. That promise was never enforced by the code.

 It was enforced by whoever held the owner key , which turned out to be the same as not enforcing it at all.

 A 2021 contract sat loaded with millions in LP token s from projects across the 2021 launch cycle, unmaintained and unmonitored , while the industry moved on and the people who controlled it apparently did not. 

 When that key changed hands, the locks became decorations. 

 Decurity saw this coming in 2023 . They documented it, disclosed it, negotiated through friction to get DxSale to act, and received $500 for their trouble . The fix that followed left the owner key exposure completely intact , a fact that Decurity stated plainly in their disclosure.

 Three years of silence followed.

 Then $7.3 million left , the primary locker was emptied to zero , and two more contracts holding a confirmed $15.5 million in LP tokens, 0x81E0eF68 and 0x2D045410 , remain under attacker control at time of publication, with no indication DxSale has taken steps to revoke that access.

 A second tweet arrived on May 30 , blaming BSC's atomic transaction feature. No post-mortem. No compensation plan. No explanation of who transferred that ownership key or why. 

 The broader lesson isn't new. Timelocks, multisig controls, and ownership monitoring are not exotic security measures - they are table stakes, documented and freely available, that would have made this specific attack structurally impossible. They weren't there. 

 The contract that held millions in other people's assets was governed by a single key with no checks on how it could be used or transferred, and that was apparently fine until it wasn't.

 DxSale's silence since the drain may yet be broken by a post-mortem, a recovery plan, or a law enforcement disclosure.

 Until then, the on-chain record is the only version of events available, and it tells a story of a nine-month setup , a controlled execution, and a team that has had little to say about any of it . 

 If your liquidity is locked in a contract where the owner can unlock it whenever they want, is it really locked, or are you just trusting a stranger with your keys? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
