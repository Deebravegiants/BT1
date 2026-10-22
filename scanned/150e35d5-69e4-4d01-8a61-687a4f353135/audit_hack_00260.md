# [H] Tapioca DAO exploit: Another day, another private key theft, another protocol rekt

## Summary
Severity: High
Target: Tapioca DAO
Loss: $4,400,000
Published: 10/18/2024
Source: https://rekt.news/tapioca-dao-rekt
Type: rekt-postmortem

## Details
## Tapioca DAO - Rekt

 Monday, October 21, 2024 Tapioca DAO - REKT 

 read this article also in : 

 Another day, another private key theft, another protocol rekt. 

 Tapioca DAO on Arbitrum suffers a roughly $4.4 million loss in a private key compromise. 

 Some funds have been recovered, though the full extent of the damage remains to be seen, though the full extent of the damage remains to be seen.

 Seems like Tapioca's recipe for success didn't include robust key management.

 The attacker, playing the role of a master chef, cooked up a scheme that left Tapioca's defenses as mushy as overcooked noodles. 

 While the protocol scrambles to reassure users, whispers of a notorious hacker group are already circulating through the cryptosphere.

 Did Tapioca have a North Korean dev in their pocket, or just a bad case of compromised keys?

 These hackers are hitting us from all angles - yesterday's Radiant Capital got served a steaming hot plate of RAT malware , and now Tapioca's security is looking more half-baked than a botched soufflé. 

 In this DeFi kitchen nightmare, are we watching the evolution of financial warfare, or just the same old recipe of greed and incompetence, now with a side of state-sponsored hacking? 

 Credit: Daniel VF , 0xTeun , ZachXBT , Tapioca DAO , Hacken , Bleeping Computer , The Block 
 As the crypto world slumbered, 0xTeun sounded the alarm : Tapioca was under attack. 

 Seems our enterprising hacker managed to exploit the Emergency Rescue function on one of the Vesting contracts deployed by the Tapioca Deployer.

 Another day, another vulnerability laid bare.

 The attacker wasted no time, exploiting the vulnerability to withdraw roughly 30 million TAP tokens.

 With the finesse of a seasoned trader, they swapped this haul for 591 ETH, sending TAP's value into a 97% nosedive . 

 But why stop there? Our hacker friend wasn't done cooking. 

 They multi-called several other addresses including the $USDO stablecoin contract and minted themselves a jaw-dropping five quintillion $USDO.

 Because why settle for millions when you can have quintillions?

 Following the crypto equivalent of a high-speed chase, our blockchain sleuths tracked the stolen funds as they were bridged to the BNB Chain.

 As of press time, the suspicious address sits pretty with approximately $4.4 million in stablecoins like BSC-USD and USDC. Not a bad day's work for our digital desperado.

 Tapioca DAO finally broke their silence - a mere 6 hours after the attack. 

 Their official response? A classic case of "it's not a bug, it's a feature." 

 According to Tapioca, this wasn't just any old hack - oh no, this was a "social engineering attack."

 Apparently, the attacker managed to compromise the TAP token vesting contract's ownership, allowing them to claim and sell a whopping 30M vested TAP .

 But wait, there's more! The USDO stablecoin contract's ownership was also compromised, with the attacker adding a minter to infinite mint USDO and drain the USDO/USDC LP pair.

 Tapioca's damage report ? A cool 591 ETH and 2.8M USDC stolen. At least they're consistent with the blockchain detectives on this one. 

 The attack centered on Tapioca's vesting contract, a piece of code that was supposed to keep tokens locked up tight. 

 TAP Vesting Contract: 
 0x2997C5ddD3070A46E9938261ce0A16a237121cb0 

 Exploiter: 
 0x70285a11489bed93686410EBC727057CAfb8129D 

 Attack Transaction 1: 0x8cf8def40fa2beab66f46863478bea71ad8f4512003caf2fa639cc5a00550753 

 Attack Transaction 2: 0x1abb8cf0b0af2ce19a30ce5103d51269d4600d9aeba045260feb588db89d76a4 

 Attack Transaction 3: 

 0x174c3deaf563be1bb6d873ba279421e8588acc888ef672bafd5efe7441aae74f 

 But our hacker wasn't satisfied with just one course. For dessert, they set their sights on Tapioca's stablecoin, turning USDO into their personal money printer. 

 USDO Stablecoin Contract: 

 0xEB99062643cA5Ab880c077288345E0B14B297432 

 USDO Infinite Mint Exploit: 

 0x0bca43cfb5b14ea039f2b329cb6074383d54ed8240963014ccb6400befa5a4e3 

 Stolen funds were bridged from Arbitrum to BSC: 
 0x69d91e56ca80f2a4d7b808b59053ea5c5505ffe2 

 But wait, there's more! Our favorite on-chain sleuth, ZachXBT, has stirred the pot with some spicy observations . 

 According to Zach, this Tapioca tempest might be connected to a string of recent hacks targeting projects like Nexera, Concentric, Masa, SpaceCatch, and others. 

 The common ingredient in this hacker's cookbook?

 Malware, possibly served up through fake job listings.

 It seems in the world of DeFi, "We're always hiring!" could be code for "We're always hacking!"

 And here's where it gets really interesting - Zach hints at a potential connection to everyone's favorite boogeyman of the crypto world: North Korean state-sponsored hackers. 

 But just when you thought this story couldn't get any wilder, Tapioca serves up a plot twist that would make M. Night Shyamalan jealous. 

 In a stunning turn of events, they've managed to pull a reverse uno card on the hacker.

 Tapioca announced in their Discord : "We have hacked the hacker! Recovered 1000 ETH which is now safely in the DAO multisig. The 1000 ETH was DAO collateral within Big Bang Origins to mint USDO for USDO/USDC LP."

 With this recovery, Tapioca's treasury now stands at $4.2M.

 The team promises more details in the upcoming post-mortem, crediting Seal911 and EnigmaDarkLabs for their assistance in this counter-operation. 

 As Tapioca continues to work on resolving the situation, this story is far from over and should make for another interesting post mortem. 

 And because no crypto disaster is complete without a side of phishing, scammers quickly moved in, impersonating Tapioca DAO and dropping malicious links like breadcrumbs.

 Hacken's warning to users? Don't take the bait.

 Well, somebody took the bait. But was it a Tapioca team member who swallowed the phishing hook, line, and sinker? 

 Did our hacker chef serve up a specially crafted "job opportunity" that was too tasty to resist? 

 After Tapioca's $4.4 million stumble, we're left with a familiar taste of incompetence garnished with a side of North Korean intrigue. 

 It's another entry in the "How Not to DeFi" handbook, where your protocol is just one compromised key away from being the next cautionary tweet thread. 

 The security game has leveled up, evolving from smart contract bug hunts to a twisted version of "Who's the Mole?"

 While we've gotten better at auditing our code, we've forgotten to run a virus scan on our devs.

 Rogue actors aren't just in our programs anymore; they're writing them. 

 They're in our VS Code extensions , our job applicant pools , and probably in that weird Discord server you joined last week. 

 At this rate, every Web3 project will have their very own pet North Korean hacker by 2025.

 Forget "bring your dog to work day" - it's now "bring your state-sponsored cyber-criminal to work day."

 In this crypto clown fiesta, where your next colleague could be coding for Kim Jong-un on the weekends. 

 Is this the cyberpunk future we were promised, or just a really elaborate phishing scam that we're all falling for? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
