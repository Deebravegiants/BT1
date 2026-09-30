# [M] Tornado Cash Governance exploit: In a whirlwind of events, Tornado Cash's governance has been taken hostage via a trojan horse proposal, effectively granting control of the DAO to a s

## Summary
Severity: Medium
Target: Tornado Cash Governance
Loss: $750,000
Published: 05/20/2023
Source: https://rekt.news/tornado-gov-rekt
Type: rekt-postmortem

## Details
## Tornado Cash Governance - REKT

 Monday, May 22, 2023 Tornado Cash - Governance - REKT 

 read this article also in : 

 Cypherpunks strive to become ungovernable… 

 …but not like this. 

 In a whirlwind of events, Tornado Cash's governance has been taken hostage via a trojan horse proposal, effectively granting control of the DAO to a single address. 

 While the contracts do not allow for draining of the ~$275M in the privacy pools themselves, the exploiter gained control of the TORN governance token, the power to modify the router to reroute deposits/withdrawals, and admin status over Nova, the Gnosis chain deployment.

 However, it seems not all is lost. 

 Yesterday, just before midday UTC, the exploiter published another proposal to revert the changes. 

 As long as there are no nasty surprises this time, this could be a bullet dodged for the Tornado Cash community.

 Repentant grey-hat? 

 Lazarus intern ? 

 Or maybe the hacker is just looking to pump and dump their remaining TORN? 

 Credit: samczsun , SlowMist , BlockSec , Apoorv Lathey 

 It’s been a tough year for DeFi’s go-to crypto mixer. 

 From the OFAC sanctions levelled in August, and the jailing of core developer, Alexey Pertsev, now released pending trial.

 Last week there were worries that someone was attempting to exploit Tornado’s governance system, creating multiple addresses and locking 0 TORN to the governance vault. Given that nothing immediately came of it, it was dismissed as a failed attempt.

 Was it a decoy, perhaps? 

 Or a preparatory move? 

 Exploiter address 1: 0x092123663804f8801b9b086b03b98d706f77bd59 

 Exploiter address 2: 0x592340957ebc9e4afb0e9af221d06fdddf789de9 

 The successful attack was smuggled in under cover of a proposal to penalise certain ‘cheating’ relayers . While the code purportedly used the same logic as a previous proposal , the attacker had added an extra function which allowed them to selfDestruct the contract.

 The proposal contract itself was published via a deployer contract. By combining CREATE and CREATE2 opcodes, the attacker could take advantage of their deterministic deployment to deploy new code into the address approved by governance.

 Using selfDestruct , the hacker was then able to erase the approved code, simultaneously resetting their nonce, and allowing for a redeployment of the malicious contract at the same address.

 BlockSec’s Yajin Zhou explains :

 Option I: Use CREATE2 opcode to create a malicious proposal contract. This will raise a flag since CREATE2 and self-destruct are used together.

 Option II: Use CREATE2 to create the deployer contract (0x7dc8), which further deploys the malicious proposal contract (0xc503) using CREATE.

 Then the deployer contract is self-destructed (to reset the nonce), and it can create a new proposal at the same address (0xc503).

 4/ That's because the address of the deployed contract using CREATE depends on the sender and nonce (nonce = 1), enabling the attacker to create a new proposal with the same address (0xc503)

 These techniques for creating ‘ metamorphic contracts ’ are one reason that some have called for the selfDestruct opcode to be deprecated. 

 The malicious proposal then assigned 10,000 TORN to all addresses created in last week’s ( presumed ) failed exploit. These were unlocked and withdrawn from the vault, granting the exploiter 1.2M votes (against 700k legitimate votes) and full control of Tornado governance.

 See BlockSec’s chart for a full breakdown of the attack stages:

 In unexpected turn of events, the exploiter later published a proposal to revert the effects of their hostile takeover, handing back control to the DAO as before. 

 Apart from the 430 ETH (~$750k) profit from dumping TORN ( any guesses where the attacker chose to launder the profits? ), the hacker may have other motivations :

 Either they're giga trolling or it will end up being an expensive but not disastrous lesson in Governance security.

 As community member Tornadosaurus-Hex pointed out :

 I mean note that we don’t even have a choice in regards to this proposal but it is still important nonetheless.

 Hopefully, this devastating (albeit impressively crafted) exploit will have a happy ending. 

 Should it have been spotted? Maybe. 

 But with recent trouble amongst contributors , perhaps the DAO was not at full strength.

 The warning “ You will be at the helm of negligent tokenholders. ” reads as stunningly prescient, in hindsight.

 However we got here, hopefully this all turns out to have been nothing more than a storm in a teacup .

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
