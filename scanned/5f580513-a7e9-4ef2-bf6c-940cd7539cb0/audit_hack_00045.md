# [H] Bittensor exploit: On July 2, Bittensor's blockchain enlightenment was rudely interrupted by a $8 million hack, due to a compromised PyPi Package Manager

## Summary
Severity: High
Target: Bittensor
Loss: $8,000,000
Published: 07/02/2024
Source: https://rekt.news/bittensor-rekt
Type: rekt-postmortem

## Details
## Bittensor - Rekt

 Wednesday, July 3, 2024 Bittensor - Rekt 

 read this article also in : zh 

 On July 2, Bittensor's blockchain enlightenment was rudely interrupted by a $8 million hack, due to a compromised PyPi Package Manager. 

 As validators meditated on their nodes, an attacker silently drained their wallets faster than you can say "om." 

 The path of the TAO led straight to the hacker's wallet, with approximately 32,000 TAO tokens making an unauthorized journey.

 The Bittensor team swiftly responded to the situation by immediately halting all network operations, taking decisive action to address the issue at hand. 

 The network entered "safe mode," allowing blocks to be produced but preventing any transactions from being processed.

 This measure was taken to prevent further losses and protect users while a thorough investigation is conducted.

 The incident led to a swift 15% decline in the value of the TAO token, demonstrating that in blockchain, as in life, everything flows... including market cap.

 According to Bittensor’s Telegram , users and stakers are fine. It's just the owners of some validators, subnets and miners that were drained. 

 Ready to unpack this clusterbleep of cosmic proportions? 

 Credit: Bittensor , ZachXBT

 Bittensor initially announced in their Discord that a number of their wallets were attacked, going on to state that they’re investigating and have halted all on-chain transactions as a precaution. 

 The attack on Bittensor's blockchain unfolded with the precision of a well-practiced qigong routine.

 Over a mere 3-hour span, the attacker managed to compromise multiple high-value wallets, making off with approximately 32,000 TAO tokens.

 As the Bittensor team scrambled to respond, the crypto community's favorite on-chain sleuth was already on the case.

 Shortly after the theft, ZachXBT identified the address that stole the funds: 

 5FbWTraF7jfBe5EvCmSThum85htcrEsCzwuFjG3PukTUQYot

 Zach, ever the crypto detective, may have tied it to a previous incident on June 1st, where a TAO holder had over 28k TAO stolen , worth $11.2M at the time of the theft. 

 The day after the attack, the Opentensor Foundation (OTF) dropped their post-mortem , revealing the root cause of the attack was a compromised PyPi Package Manager.

 Here's how this digital dumpster fire unfolded: 

- 
 A malicious package, masquerading as a legitimate Bittensor package, snuck its way into PyPi version 6.12.2.

- 
 This trojan horse contained code designed to steal unencrypted coldkey details.

- 
 When unsuspecting users downloaded this package and decrypted their coldkeys, the decrypted bytecode was sent to a remote server controlled by the attacker.

 The vulnerability affected users who downloaded the Bittensor PyPi package between May 22 and May 29, or used Bittensor==6.12.2, and then performed certain operations like staking, unstaking, transferring, delegating, or undelegating.

 In response to the attack, the Bittensor team quickly put the chain into "safe mode”, halting all transactions while continuing to produce blocks.

 This swift action may have prevented further losses, but it also highlighted the centralized control the team maintains over the supposedly decentralized network. 

 The OTF has taken immediate steps to mitigate the damage: 

- 
 Removed the malicious 6.12.2 package from the PyPi Package Manager repository.

- 
 Conducted a thorough review of Subtensor and Bittensor code on Github.

- 
 Worked with exchanges to trace the attacker and potentially salvage funds.

 Moving forward, the OTF has promised enhanced package verification, increased outside audit frequency, improved security standards, and increased monitoring moving forward. 

 The OTF stated that the incident did not affect the blockchain or Subtensor code, and the underlying Bittensor protocol remains uncompromised and secure. 

 They have also been working with several exchanges, providing them with details of the attack in order to trace the attacker and potentially salvage funds.

 As the dust settles, the community is left pondering how the malicious package slipped through PyPi's defenses and whether this attack is linked to the June 1st theft. 

 It seems in the world of Bittensor, the path to enlightenment is paved with some empty wallets. 

 The Bittensor hack exposes a critical vulnerability in the crypto ecosystem, the reliance on third-party package managers. 

 While blockchain protocols themselves may be secure, the tools developers use to interact with them can become unexpected points of failure. 

 This incident raises questions about the security practices of PyPi and other package repositories that the crypto community depends on.

 The timing and similarity to the June 1st theft can't be ignored. 

 Are these isolated incidents, or is there a more widespread campaign targeting Bittensor and similar projects? 

 As the OTF works with exchanges to trace the stolen funds, the community watches with bated breath, hoping for a recovery that rarely comes in the wake of such hacks.

 Bittensor's swift action in halting the network demonstrates the double-edged nature of centralized control in "decentralized" projects.

 While it may have prevented further losses, it also highlights the fragility of the system.

 In the Tao of crypto, the only constant is change and occasionally, an $8 million vanishing act. 

 As Bittensor reflects on its security practices, will they find true blockchain enlightenment or are they destined to keep laying down these expensive stepping stones on the path to a more perfect protocol? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
