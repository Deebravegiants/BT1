# [H] Radiant Capital exploit: Lending protool Radiant Capital lost 1900 ETH ($4.5M), yesterday, to a known bug affecting freshly-launched markets

## Summary
Severity: High
Target: Radiant Capital
Loss: $4,500,000
Published: 01/02/2024
Source: https://rekt.news/radiant-capital-rekt
Type: rekt-postmortem

## Details
## Radiant Capital - REKT

 Wednesday, January 3, 2024 Radiant Capital - Fork - REKT 

 read this article also in : 

 2024 is off to a bright start... 

 Lending protool Radiant Capital lost 1900 ETH ($4.5M), yesterday, to a known bug affecting freshly-launched markets. 

 Radiant, a fork of Aave V2, operates on Arbitrum and BSC, with the hack occurring on the Arbitrum deployment’s new native USDC market.

 It appears the attacker had been lying in wait, likely having identified the vulnerability in Aave-forks via updates to the Aave protocol itself. 

 The attacker’s address , as well as Discord screenshots , were posted to Twitter, raising the alarm. An official confirmation came later, adding:

 No current funds are at risk.

 So, just the $4.5M that had already been stolen, then? 

 Credit: Peckshield , Ancilia 

 The issue in forked Aave V2 code affects recently-launched (and therefore empty ) markets. 

 A potential attacker has a brief window after launch to use a flash loan to manipulate the value of collateral, thanks to the combination of a rounding error and a totalSupply value of 0.

 The exploiter wasted no time, deploying their attack contract just six seconds after the new market was activated . 

 The bug was previously mitigated in the original Aave protocol by simply including an initial deposit with the creation of new markets, ensuring they are never sitting empty.

 Given the speed of the attack, the attacker had clearly prepared everything in advance whilst waiting for the proposal to add the market (which passed on December 25th) to be enacted.

 Attacker’s address: 0x826d5f4d8084980366f975e10db6c4cf1f9dde6d 

 Attack contract: 0x39519c027b503f40867548fb0c890b11728faa8f 

 Attack tx 1: 0x1ce7e9a9… 

 Attack tx 2: 0x2af55638… 

 Attack tx 3: 0xc5c4bbdd… 

 The Radiant Team has sent an on-chain message to the hacker’s address (where funds remain), and appear confident that they’re dealing with a whitehat “ for various reasons ”.

 Despite four audits , from OpenZeppelin, BlockSec, Peckshield and Zokyo, a constantly-evolving security landscape means updates must be made in a timely manner. 

 Especially when dealing with forked code. 

 We've discussed the risks of forks plenty of times, with multiple leaderboard entries down to vulnerabilities patched in one place before being exploited elsewhere.

 When copy-pasting an established project, more eyes are focused on the original project’s larger TVL, providing an early warning system for bugs like these.

 But if lessons aren’t learned , there’s little to be done. 

 Are any other forked protocols planning to launch new markets soon? 

 Are they up to date on the risks? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
