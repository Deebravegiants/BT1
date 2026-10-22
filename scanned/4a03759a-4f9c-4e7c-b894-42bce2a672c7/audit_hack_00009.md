# [H] Aevo exploit: Six days, that was the exact shelf life of Aevo’s latest oracle upgrade before it turned their legacy Ribbon vaults into a public donation bin

## Summary
Severity: High
Target: Aevo
Loss: $2,700,000
Published: 12/12/2025
Source: https://rekt.news/aevo-rekt
Type: rekt-postmortem

## Details
## Aevo - Rekt

 Thursday, December 18, 2025 Aevo - Ribbon Finance - Rekt 

 read this article also in : 

 Six days, that was the exact shelf life of Aevo’s latest oracle upgrade before it turned their legacy Ribbon vaults into a public donation bin. 

 On December 12, the protocol bled $2.7 million , not through a complex cryptographic failure, but because of an upgrade that accidentally removed the lock from the front door . 

 This allowed the attacker to simply ask the oracle to set the price of assets to arbitrary, astronomical levels , and the contract obliged.

 This wasn't a case of neglected code gathering dust, but another example of incremental upgrades where the design choices made earlier were ignored .

 While the team focused on their new exchange, their digital attic was ransacked by someone who noticed the security controls had been updated to "optional." 

 When a routine patch turns a legacy vault into an open checkbook, is it really an exploit, or just an involuntary feature release? 

 Credit: The Block , Aevo (Previously Known as Ribbon Finance , Anton Cheng , Liyi Zhou , Blockworks , William Li , Wesley Wang , Halborn , OpenZeppelin , Web3isgoinggreat 
 It was supposed to be maintenance. 

 To understand the negligence angle, you have to understand the architecture.

 Ribbon Finance was the OG of DeFi options, but in July 2023, the DAO voted to merge into Aevo , unifying the brands and folding Ribbon’s structured products into Aevo’s suite.

 This wasn't a deprecation; it was a unification.

 The governance proposal explicitly approved "folding Ribbon Finance into Aevo's suite of structured products," rebranding the Ethereum-based vaults and integrating them as the core L1 vertical of Aevo's "DeFi Super-App" vision. 

 But rebranding the vaults didn't make them bulletproof - it just meant a single clumsy update was enough to leave the platform's bedrock defenseless. 

 On December 6, the Aevo team pushed an upgrade to the oracle configuration for their Ribbon vaults . The goal may have been standard operational housekeeping. The result was the digital equivalent of unscrewing the hinges from the bank vault.

 The upgrade inadvertently exposed the price-feed proxies , leaving critical functions like transferOwnership and setImplementation completely unprotected .

 For six days, the contract sat there, waiting for anyone with a block explorer and a lack of morals to notice. On December 12, someone finally did.

 The attacker didn't need to outsmart the market or manipulate liquidity depth. They simply promoted themselves to admin. 

 Specter flagged the carnage while the body was still warm , identifying the exploit contract and the initial outflows long before Aevo announced the hack themselves. 

 It took Aevo until the cold light of the next morning to catch up. Nearly 19 hours after the heist began, the protocol finally broke their silence , tweeting a confirmation that their legacy vaults had been "exploited following a vulnerability in a smart contract update" - corporate speak for admitting they broke their own lock.

 Researcher Liyi Zhou and former Opyn dev Anton Cheng dissected the mechanics.

 The attack began with a specific setup transaction , where the exploiter minted a financial Frankenstein: options collateralized by wstETH, but chemically bonded to AAVE as the underlying asset. 

 Under Opyn’s original Gamma protocol design, this shouldn't have been a problem . The protocol enforces strict matching rules to ensure full collateralization. Opyn wasn’t broken.

 But Ribbon’s "upgraded" configuration didn’t follow those rules .

 The flawed upgrade didn't break the rules, it rewrote them. According to William Li’s analysis , it allowed the attacker to legally whitelist arbitrary products, turning the creation of malicious markets into a valid protocol action.

 But the real damage came from how they abused the upgradeable price-feed proxies. 

 The upgrade didn't just tweak the math, it created a fatal misalignment between the protocol's past and present . While the new configuration supported 18 decimals, many older assets on the platform still used 8 decimals. 

 Worse, the proxy-based oracle stack included a critical access control vulnerability . It inadvertently permitted anyone to set expiry prices for newly-created assets .

 The attacker didn't need to outsmart the market, they just needed to exploit this math error.

 As detailed by security firm Halborn , the attacker executed the drain by creating an arithmetic monstrosity: options products that exploited the decimal precision gap.

 The attacker spun up short-fuse options with strike prices buried deep below market value. By mixing 18-decimal assets with 8-decimal relics, they turned a precision error into a precision weapon. 

 For example, the attacker created an stETH call option with a strike price of 3,800 USDC (8-decimal) , collateralized by WETH (18-decimal), and created oTokens from these . 

 When these options expired on December 12, the system's broken logic - confused by the precision mismatch - calculated that the current value of stETH was astronomically higher than the 3,800 USDC strike.

 The result was a money printer. In one instance, the attacker burned just 225 oTokens to drain approximately 22.46 WETH .They rinsed and repeated the process until the vaults were empty.

 The underlying protocol worked exactly as code is intended to work. It was Ribbon’s configuration that essentially handed the attacker a loaded gun and pointed it at their own treasury. 

 Now that the vault was open and the prices were rigged, the only question remained: how fast could they empty it? 

## The Loot Trail

 This wasn't a clumsy smash-and-grab. It was an ice cold execution. 

 Specter’s analysis reveals a professional operation , and maybe not a lone gunman. Some security reports might flag one exploiter, but on-chain flows show an org chart with a distinct separation of roles. 

 Phase 1 - The Setup: The Mastermind funded the infrastructure, but stayed out of the blast radius. Clean hands from dirty money. Instead of direct involvement, they seeded a network of wallets to assemble the weaponry.

 The Specialist (0xCf5DF51A10c097140FB3a367281A4f5313725b1F) was activated to forge the "Frankenstein" option contract - a poisoned derivative designed to weaponize decimal precision.

 The Engineer (0x9c619915fda0db49d6ec7b4224537acb872731ca) was funded to deploy the malicious oracle logic.

 The Bagman (0x4BFD5C65082171DF83fd0fBBe54aa74909529b2c) was deployed to serve as the mule that would physically interact with the vault. 

 The Mastermind (Funder): 

 0x4c0dc529C4252e7Be0Db8D00592e04f878e4F397 

 The Specialist (Frankenstein Deployer - Note: This wallet was later reused as a money mule in Phase 4): 

 0xCf5DF51A10c097140FB3a367281A4f5313725b1F 

 The Frankenstein Contract (Malicious Option Instrument): 0x8eccacbc1147fc7edc52bae135bd54f5f1950255 

 The Frankenstein Creation Transaction(Executed by The Specialist): 

 0x9b686c9d9532f224b84825d5b6c8a8c27811a33de4b0f20204aafd288304ab54 

 The Engineer (Oracle Weapon Deployer): 

 0x9c619915fda0db49d6ec7b4224537acb872731ca 

 The Engineer’s Weapon (The malicious implementation contract. It contained the code that bypassed security checks and executed the unauthorized oracle updates): 

 0xE1f09d50F733993b11bF3054bD870d688401984c 

 The Bagman (Exploit Executor Contract - This contract is what actually interacted with the vault to receive the stolen funds): 

 0x4BFD5C65082171DF83fd0fBBe54aa74909529b2c 

 Another crucial role in the setup belonged to a player we will dub The Fall Guy - This wallet was deployed to establish the "Disguise." It executed a sequence of white-glove transactions - whitelisting collateral, deploying a clean Oracle - manufacturing a history of compliance to mask the impending hit. 

 This wasn't just a setup, it was a Trojan Horse. By establishing a resume of valid interaction, the Fall Guy ensured that when the malicious script finally ran, the protocol’s defenses didn't see an enemy. They saw the boss. 

 The Fall Guy: 

 0xb594f7e7ad548f63db49665ae4e3d3f8457cf6f5 

 Disguised PriceFeedOracle: 

 0xF2Df028a81682375b27967d6de36ADA049cBDFf7 

 The Disguised PriceFeedOracle was created in this Transaction: 

 0x7182dcc5fe69c888dbf929794c2b19450035b4e11b318218d531acea1aa31e31 

 Phase 2 - The Hijack: The kill shot came with a single transaction that rewrote the oracle’s reality. Researcher Liyi Zhou identified the weapon - a contract hammering the Proxy Admin (0x9D7b) to execute transferOwnership and setImplementation at will.

 Proxy Admin: 

 0x9D7b3586f361e3621Bf4F099cBC9d155e8ae6B76 

 Crucially, this wasn't a brute-force assault. It was a VIP entry. Technical analysis of the Proxy Admin reveals a fatal logic flaw : the transferOwnership function didn't verify the contract calling it, but simply checked for a permission flag on tx.origin. 

 The Fall Guy wallet possessed this flag. The system didn't surrender because it was overwhelmed; it surrendered because it recognized the attacker as the boss. 

 Armed with this silent authorization, the attacker triggered the sequence.

 Using the Attack Contract as a proxy, they executed a looping script that abused this access in real-time. For each asset, the script swapped the oracle implementation to the Engineer’s Weapon, forced an arbitrary price update, and immediately swapped back to the legitimate contract to mask the intrusion.

 Oracle Manipulation Transaction: 0xb73e45948f4aabd77ca888710d3685dd01f1c81d24361d4ea0e4b4899d490e1e 

 The manipulation wasn't subtle. In a single fatal transaction, the attacker swapped the oracle to point at the Engineer's Weapon. This malicious code overwrote the oracle's reality, cranking the AAVE price to infinity and locking the expiry timestamp to 1765526400 (Dec 12, 2025) .

 Phase 3 - The Drain: With the timeline hacked and prices rigged to god-mode, the protocol didn't just enable the theft - it executed the drain with the cold efficiency of a compliant machine.

 The Bagman contract immediately began the extraction. In the primary drain transaction, it burned the Frankenstein oTokens to trigger a massive payout of 846 WETH and 178k USDC from the victim vault. 

 The Bagman Contract: 

 0x4BFD5C65082171DF83fd0fBBe54aa74909529b2c 

 The Compromised Vault (Victim): 

 0x3c212A044760DE5a529B3Ba59363ddeCcc2210bE 

 Primary Drain Transaction (Confirmed by Specter trace: The Bagman burns oTokens -> Victim sends ~$2.6M in assets): 0x16eded2553e0793472a6283093738152de1dd0e2504836856fbcaf88cc4a2687 

 Address that Conducted the Drain: 

 0x657CDEfc7ef8b459b519dEFc8BED2A67d3cC1aAb 

 Phase 4 - The Getaway: Once the protocol was drained, the funds didn't stay put. They were moved to a Distributor wallet, which then blasted them out to a laundry list of theft addresses in precise 100.1 ETH batches (99 + 1 + 0.1) to prep for Tornado Cash.

 The Distributor (Consolidator): 

 0x354ad0816de79E72452C14001F564e5fDf9a355e 

 The Swarm (Laundering Mules and other Exploit Wallets): 

 0x354ad0816de79E72452C14001F564e5fDf9a355e 0x2Cfea8EfAb822778E4e109E8f9BCdc3e9E22CCC9 0x255b29642d1B125a0Ce8529aae61Ad19EE636DDf 0x537dee211543CC9CdEcB8690c5Be248D5b287558 0x46300aA369A59139E70F8Ec75ee9B921e5fdfC6F 0x816f6c6cc941364e3d2DA79442310e385043B479 0xB4f7eD0d3eA5256fA5Dfb2C73a1661ffb7f7beDb 0x40B31Ae97468e9Abd56965D1a3e28DDE1c79d0A3 0xDaDfe088422335C7A49D1de2B439e29Cb90EA5Ca 0x936457bEE1366e0bf05Eb52BB4a9FFFe2e7eF465 0x49CC128345bCF31A02b1B2B81f836f72E24c97bC 0xCf5DF51A10c097140FB3a367281A4f5313725b1F (The Specialist reused)

 Clearly, the attacker did their homework. This wasn't a panic dump, but a disciplined dispersal. By the time the security teams woke up, the trail was already cold, and the only evidence left was the on-chain equivalent of a middle finger. 

 The vault is empty, the addresses are washed, and the oracle is offline - so who exactly is left to pick up the tab? 

## The Response Pivot

 After the news hit, Aevo didn't waste time trying to patch the unpatchable. They simply pulled the plug . 

 All Ribbon vaults were immediately decommissioned . The tweet that announced both has since been deleted, along with their initial compensation plan. 

 Aevo initially laid out a compensation plan , but the kickback was so bad that they backtracked and deleted the posts about it entirely.

 Users were being offered a withdrawal with a bit of a haircut. Aevo was proposing that withdrawals be subject to only a 19% reduction on the user's position's value at hack time.

 Aevo’s initial compensation plan relied on two pillars. First, the DAO was going to forfeit its own vault positions - roughly $400,000 in assets - to absorb some of the impact. A noble gesture, but one that only covers a fraction of the $2.7 million hole.

 The real subsidy would have come from the dead. 

 The protocol explicitly stated that many of the largest depositors have been dormant for 2–4 years . These are wallets that deposited during the DeFi summer of yesteryear and seemingly forgot they exist. 

 Aevo was banking, literally, on the assumption that these "zombie" users will simply never show up to claim their money.

 But then they had a change of heart or a twist of the arm.

 Ribbon issued a stunning correction admitting their initial analysis was "fundamentally flawed, " replacing the haircut proposal with a brutal binary: if you had already queued a withdrawal, you are safe; if your funds were "active," they may be gone.

 In the end, the attempt to engineer a soft landing via 'zombie' subsidies collapsed, revealing that for the active depositors, there was never a haircut to debate. 

 When the only winning move is to withdraw before the team realizes they’re broke, are we actually engaging in decentralized finance, or just a digitized bank run? 

 There is no retirement home for smart contracts, only crime scenes waiting to happen. 

 Aevo is just the latest chapter in the "Zombie Vault" saga, joining Yearn and Balancer in the expensive lesson that old code is often just a liability with a pulse. 

 That 2021 OpenZeppelin audit might as well have been written in hieroglyphics.

 While it rigorously stress-tested the original Ribbon V2 logic against the threats of yesterday, it offered zero protection when a sloppy maintenance patch in 2025 cracked the hull, bypassing years of security hardening in a single commit. 

 It’s the digital equivalent of parking an old clunker in the driveway and forgetting about it - eventually, someone stops admiring the paint job and starts stripping it for parts.

 As protocols chase the shiny new yields of L2s and "v3" deployments, they leave these ghost towns behind, fully funded but barely guarded.

 "Deprecated" creates a false sense of security, implying a safety that no longer exists for code that is very much alive and solvent. 

 If the industry's strategy for old code is "ignore it until it breaks," how many more millions need to vanish before others learn to clean out the garage? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
