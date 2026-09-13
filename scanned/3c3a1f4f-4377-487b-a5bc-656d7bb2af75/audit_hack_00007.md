# [H] Abracadabra - Rekt III exploit: Abracadabra just performed their third disappearing act in under two years, with $1.8 million in MIM tokens vanishing through a vulnerability so obvio

## Summary
Severity: High
Target: Abracadabra - Rekt III
Loss: $1,800,000
Published: 10/04/2025
Source: https://rekt.news/abracadabra-rekt3
Type: rekt-postmortem

## Details
## Abracadabra - Rekt III

 Monday, October 6, 2025 Abracadabra - MIM - Logic Bug 

 read this article also in : 

 Three strikes and you're... still planning future deployments? 

 Abracadabra just performed their third disappearing act in under two years, with $1.8 million in MIM tokens vanishing through a vulnerability so obvious it practically had a neon sign pointing at it. 

 A simple two-action sequence - borrow, then reset the security flag - turned deprecated CauldronV4 contracts into an ATM for anyone who bothered reading the code.

 Saturday's exploit targeted six "deprecated" cauldrons on Ethereum mainnet, contracts that hadn't seen an audit since November 2023 yet somehow remained live, accessible, and perfectly capable of minting unbacked stablecoins.

 Magic Internet Money lived up to its name once again, disappearing faster than trust in a protocol that's lost over $21 million to exploits while insisting everything's under control. 

 When your security strategy consists of calling old contracts "deprecated" but forgetting to turn them off, who's really getting played? 

 Credit: William Li , BlockSec Phalcon , GoPlus Security , The Block , MIM Spell , DK27ss , Synnax 
 Saturday turned into an expensive debugging session for Abracadabra. 

 Security researcher William Li spotted it first on October 4th , dropping a preliminary analysis on Twitter.

 BlockSec Phalcon jumped in with confirmation a few hours later , flagging the exploit pattern spreading across multiple cauldron addresses.

 The cook() function's shared status tracker let actions overwrite each other's security flags - action 0 could reset needsSolvencyCheck to false, bypassing the insolvency check entirely.

 GoPlus Security tracked 51 ETH laundering through Tornado Cash while another 344 ETH sat untouched in the attacker's wallet , as if they were taking their time deciding what to do with phase two. 

 Abracadabra's response came shortly after , delivered not through their official Twitter account, but via Discord contributor 0xMerlin. 

 The message hit all the standard notes : vulnerability discovered, DAO treasury mobilized, affected MIM bought back, no user funds lost, everything under control.

 Two days after the exploit, they finally announced the hack publicly on Twitter .

 They paused all cauldron borrowing "as we review the current codebase for future upcoming deployments" - a phrase that sounds suspiciously like planning expansion while still sweeping up glass from the last break-in.

 They doubled down on the "relatively small impact" framing, as if $1.8 million and three exploits in two years qualified as minor paperwork issues. 

 But how does a protocol with multiple audit rounds, two previous multi-million dollar hacks, and a $154 million TVL end up with a vulnerability this elementary still sitting in production code? 

## The Technical Sleight of Hand

 Abracadabra's CauldronV4 uses a cook() function that bundles multiple operations into one transaction. 

 Each action gets an ID number and executes in order , with a shared status tracker deciding whether the contract needs to check if you're actually solvent before the transaction completes. 

 ACTION_BORROW (action 5) kicks off a borrow and flips needsSolvencyCheck to true - basically telling the contract "hey, verify this person has collateral before you let them leave with our money."

 Action 0 (ACTION_CUSTOM) calls an internal helper function named _additionalCookAction() - which despite its official-sounding name, does absolutely nothing except return a fresh CookStatus struct with all fields reset to false.

 solidityfunction _additionalCookAction(CookStatus memory, bytes memory) internal pure returns (CookStatus memory) {return CookStatus(false);
}

 That's the whole function . A reset button for security checks, sitting in production code like someone left a master key under the doormat. 

 The attacker's execution was efficient : call cook() with actions = [5, 0], pass in parameters for a massive borrow, watch as Action 5 sets the solvency flag to true, then watch Action 0 immediately overwrite it back to false.

 When cook() finishes and checks if (status.needsSolvencyCheck) _ensureSolvent(user);, the flag reads false, the check gets skipped, and the attacker walks away with 1,793,755 MIM tokens borrowed against exactly zero collateral.

 Attacker’s Address: 

 0x1AaaDe3e9062d124B7DeB0eD6DDC7055EFA7354d 

 They repeated this sequence across six different cauldrons , treating Abracadabra's lending markets like a self-service money printer: 

 0x46f54d434063e5F1a2b2CC6d9AAa657b1B9ff82c 

 0x289424aDD4A1A503870EB475FD8bF1D586b134ED 

 0xce450a23378859fB5157F4C4cCCAf48faA30865B 

 0x40d95C4b34127CF43438a963e7C066156C5b87a3 

 0x6bcd99D6009ac1666b58CB68fB4A50385945CDA2 

 0xC6D3b82f9774Db8F92095b5e4352a8bB8B0dC20d 

 Attack transaction: 0x842aae91c89a9e5043e64af34f53dc66daf0f033ad8afbf35ef0c93f99a9e5e6 

 The attacker skipped the complex stuff, no multi-step transaction gymnastics.

 Just two actions in the right order , exploiting a logic flaw anyone with access to the contract code could've spotted. 

 Precision errors and rounding bugs require PhD-level math to exploit; this vulnerability just needed someone willing to read the code and ask "wait, what happens if I do this?" 

## Follow the Money

 The attacker didn't materialize from nowhere - Tornado Cash provided the introduction. 

 Once the vulnerability was identified, execution followed a predictable pattern across six cauldrons. 

 Tornado Cash Funding: 

 0x68437f1f687e3fbe65dd86a802f6ca08b44af3dff612f02c4c8b6945c9dd4f82 

 Attacker also used this wallet to send the funds from Tornado Cash: 

 0x1FF8Ea9b29aa10713774b60134D53529301Ca9C5 

 Primary Attacker Address: 

 0x1AaaDe3e9062d124B7DeB0eD6DDC7055EFA7354d 

 Attack Contract (self-destructed): 

 0xB8e0A4758Df2954063Ca4ba3d094f2d6EdA9B993 

 Exploited DegenBox: 

 0xd96f48665a1410c0cd669a88898eca36b9fc2cce 

 Funding came from Tornado Cash - because nothing says "legitimate research" quite like mixing your seed ETH through sanctioned privacy protocols before draining lending markets.

 The attacker worked methodically through six cauldrons , minting 1,793,755 MIM against zero collateral. Once the unbacked stablecoins were secured, they converted roughly half to ETH and started the standard exit routine: swap, bridge, Tornado.

 51 ETH hit the mixer immediately while 344 ETH remained parked in the attacker's wallet , but only for a couple of minutes, as all of the ETH was laundered through Tornado Cash in over 3 dozen transactions.

 Tornado Cash Laundering: 

 0x1aaade3e9062d124b7deb0ed6ddc7055efa7354d 

 Abracadabra's DAO treasury stepped in with a buyback operation , purchasing the dumped MIM from the market and claiming they'd "completely reversed the effect of the attack." 

 The buyback transaction: 0xbaede1ddbab71fb48d25139e720356d8c487d47ce4b94aaf683969dc1fb1c984 

 Their narrative leaned hard on "no user funds lost" - which is only true if DAO treasury reserves don't count as anyone's money.

 But treasury funds don't materialize from thin air; they're stakeholder assets that could've funded security audits, development, or literally anything besides covering losses from entirely preventable exploits.

 Calling it "relatively small impact" while burning through treasury funds to patch a $1.8 million hole is like calling a car crash minor because insurance covered it. 

 When your damage control strategy relies on redefining whose money counts as "real" losses, what exactly are you protecting? 

## The Audit That Wasn’t

 Abracadabra's GitHub audit folder reads like a timeline of looking everywhere except where it mattered. 

 November 14, 2023: Guardian Audits reviewed GMXV2 CauldronV4 - a specialized variant that got gutted for $13 million 16 months later. 

 February 6, 2024: LockingMultiRewards audit .

 March 21, 2024: MIMSwap audit - shiny new product gets immediate attention.

 December 16, 2024: BoundSpell audit .

 Spot what's absent? 

 Any recent security review of the base CauldronV4 contracts - the ones actually processing borrows on Ethereum mainnet, the ones labeled "deprecated" but somehow still live and functional. 

 The last time auditors examined standard CauldronV4 logic was November 2023 , almost two years before this October exploit.

 Between that audit and Saturday's attack, Abracadabra commissioned security reviews for their shiny new features while the foundation sat untouched, unexamined, and apparently unfixable.

 Two major hacks happened during that window - $6.5 million in January 2024 , $13 million in March 2025 - yet audit resources kept flowing toward expansion rather than securing what already existed.

 Code4rena found 20 vulnerabilities during their March 2024 MIMSwap review , including four rated high severity. 

 Note: this review focused exclusively on the new MIMSwap module and did not include the core CauldronV4 contracts that handle Ethereum mainnet borrows - the contracts ultimately exploited in October 2025. 

 This highlights a pattern: security resources were concentrated on new features while foundational logic remained largely unexamined.

 Then there's the PeckShield situation - a masterclass in transparency theater.

 Synnax Labs, an Abracadabra fork, shared the same vulnerable codebase.

 PeckShield audited them in November 2024 , missed the attack vector entirely, reported two medium and two low severity issues, called it secure. 

 3 days before the Abracadabra exploit, Synnax paused their contracts for "security upgrades." 

 Eighteen hours before the attack, PeckShield quietly deleted their Synnax audit report from GitHub .

 After Synnax requested and received a refund for the failed audit , the report vanished from public view - though git history never forgets.

 William Li documented the whole sequence : audit published, vulnerability exploited on similar codebase, audit deleted, refund issued, everyone pretends it never happened.

 PeckShield's post-exploit silence spoke louder than any alert they didn't send. 

 Companies that miss critical vulnerabilities usually release detailed post-mortems explaining what went wrong; companies that delete evidence and ghost the community are protecting their reputation, not their clients. 

 Synnax Labs - Abracadabra's own fork - discovered this vulnerability and paused contracts four days before the attack.

 PeckShield deleted their audit report eighteen hours before the exploit hit.

 The warning signs were public, the codebase was shared, and Abracadabra's deprecated contracts kept running.

 "Deprecated" became a convenient label for contracts they'd stopped maintaining but never bothered to shut down - like calling a loaded gun "decorative" and leaving it on the coffee table. 

 When your fork pauses contracts four days before your exploit, PeckShield deletes their audit, and you've already bled $19.5 million across two previous hacks - what part of "deprecated" gave anyone confidence these contracts were safe? 

 Three times rekt, $21 million lighter, still insisting it's all under control. 

 Abracadabra's magic was supposed to be turning idle collateral into yield - turns out the real trick is making protocol funds vanish while claiming victory. 

 $6.5 million vanished through rounding errors, $13 million leaked through phantom collateral, and now $1.8 million walked out the door via a status flag anyone could flip - each exploit more preventable than the last, each response more hollow than the previous.

 Their audit folder documents everything except the contracts that mattered, their "deprecated" label meant "ignored but still live," and their damage control playbook reduces to treasury buybacks and semantic debates about whose funds actually count as lost.

 Magic Internet Money hasn't just been hacked 3 times - it's become a case study in how protocols prioritize expansion over maintenance, new features over fundamental security, and optics over accountability.

 $21 million in cumulative losses later, they're still planning "future deployments" while sweeping up glass from exploits that never should have happened. 

 When your third disappearing act is the easiest one yet, what's the real magic trick - the exploits, or convincing anyone there's still a protocol worth trusting? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
